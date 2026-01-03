"""
Generation Router - API Endpoints for CV Generation
Handles batch generation, status tracking, model selection, and file management
"""

import os
import asyncio
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional

from ..core.task_manager import task_manager, Task, TaskStatus
from ..core.pdf_engine import render_cv_pdf, generate_pdf_from_existing_html
from ..services.llm_service import generate_cv_content_v2, generate_profile_data, get_available_models as get_llm_models, create_user_prompt
from ..services.krea_service import generate_avatar, get_available_models as get_image_models, get_avatar_prompt

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BACKEND_DIR / "output"
ASSETS_DIR = BACKEND_DIR / "assets"

# Organized output subdirectories
PROMPTS_DIR = OUTPUT_DIR / "prompts"
HTML_DIR = OUTPUT_DIR / "html"
PDFS_DIR = OUTPUT_DIR / "pdfs"
AVATARS_DIR = OUTPUT_DIR / "avatars"

# Ensure all directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)
PROMPTS_DIR.mkdir(exist_ok=True)
HTML_DIR.mkdir(exist_ok=True)
PDFS_DIR.mkdir(exist_ok=True)
AVATARS_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/api", tags=["generation"])


# Request/Response Models
class GenerationRequest(BaseModel):
    qty: int = Field(ge=1, le=50, default=1)
    genders: list[str] = Field(default=["any"], description="List of genders: male, female, any")
    ethnicities: list[str] = Field(default=["any"], description="List of ethnicities")
    origins: list[str] = Field(default=["any"], description="List of regions/countries")
    roles: list[str] = Field(default=["Software Developer"], description="Custom role tags - any text allowed")
    age_min: int = Field(ge=18, le=70, default=25, description="Minimum age")
    age_max: int = Field(ge=18, le=70, default=35, description="Maximum age")
    expertise_levels: list[str] = Field(default=["mid"], description="junior, mid, senior, expert")
    remote: bool = Field(default=False, description="Include remote work preference")
    # New separate models
    profile_model: Optional[str] = Field(default=None, description="LLM for Profile Generation")
    cv_model: Optional[str] = Field(default=None, description="LLM for CV Content")
    # Legacy fallback
    llm_model: Optional[str] = Field(default=None, description="Fallback LLM model")
    image_model: Optional[str] = Field(default=None, description="Krea model ID")


class GenerationResponse(BaseModel):
    batch_id: str
    message: str
    total_tasks: int


class ModelInfo(BaseModel):
    id: str
    name: str
    description: str


class ModelsResponse(BaseModel):
    llm_models: list[dict]
    image_models: list[dict]


class FileInfo(BaseModel):
    filename: str
    path: str
    created_at: str
    size_kb: float


class FilesResponse(BaseModel):
    files: list[FileInfo]
    total: int

# Store selected models per batch
batch_models = {}


async def process_batch(batch_id: str, profile_model: Optional[str], cv_model: Optional[str], image_model: Optional[str]):
    """Execute the sequential 4-Phase Generation Pipeline."""
    batch = task_manager.get_batch(batch_id)
    if not batch: return
    
    tasks = batch.tasks
    
    # --- PHASE 1: GENERATE UNIQUE PROFILES ---
    # Concurrency: 5 (Fast, text only)
    print(f"=== STARTING PHASE 1: PROFILES ({len(tasks)} tasks) ===")
    
    sem_phase1 = asyncio.Semaphore(5)
    
    async def run_phase1(task: Task):
        async with sem_phase1:
            try:
                task.status = TaskStatus.RUNNING
                task.current_subtask_index = 0
                task.subtasks[0].status = TaskStatus.RUNNING
                task.subtasks[0].message = "Inventing unique persona..."
                await task_manager._save_batches()
                
                profile_data, prompt = await generate_profile_data(
                    role=task.role,
                    gender=task.gender,
                    ethnicity=task.ethnicity,
                    origin=task.origin,
                    age_range=task.age_range,
                    model=profile_model
                )
                
                # Save Profile Data to Task
                task.profile_data = profile_data
                
                # Update status
                task.subtasks[0].status = TaskStatus.COMPLETE
                task.subtasks[0].progress = 100
                task.progress = 20
                task.message = f"Profile Created: {profile_data.get('name')}"
                await task_manager._save_batches()
                
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.ERROR
                task.subtasks[0].status = TaskStatus.ERROR
                print(f"Phase 1 Error Task {task.id}: {e}")

    await asyncio.gather(*[run_phase1(t) for t in tasks])
    
    # Check if we should proceed (at least one success)
    active_tasks = [t for t in tasks if t.status != TaskStatus.ERROR]
    if not active_tasks:
        print("Batch failed at Phase 1")
        return

    # --- PHASE 2: GENERATE CV CONTENT ---
    # Concurrency: 3 (Heavy LLM work)
    print(f"=== STARTING PHASE 2: CV CONTENT ({len(active_tasks)} tasks) ===")
    sem_phase2 = asyncio.Semaphore(3)
    
    async def run_phase2(task: Task):
        async with sem_phase2:
            try:
                task.current_subtask_index = 1
                task.subtasks[1].status = TaskStatus.RUNNING
                task.subtasks[1].message = "Writing detailed CV..."
                task.status = TaskStatus.GENERATING_CONTENT
                await task_manager._save_batches()
                
                # Use Profile Data from Phase 1
                p = task.profile_data or {}
                
                cv_data, used_prompt = await generate_cv_content_v2(
                    role=p.get('role', task.role),
                    expertise=task.expertise, # Keep expertise from request
                    age=p.get('age', 30),
                    gender=p.get('gender', task.gender),
                    ethnicity=p.get('ethnicity', task.ethnicity),
                    origin=p.get('origin', task.origin),
                    remote=task.remote,
                    model=cv_model,
                    name=p.get('name'), # Pass name explicitly
                    profile_data=p # Pass full profile mainly for consistency 
                )
                
                task.cv_data = cv_data
                
                # Save Prompt
                try:
                    path = PROMPTS_DIR / f"{task.id}_cv_prompt.txt"
                    with open(path, "w", encoding="utf-8") as f: f.write(used_prompt)
                except: pass

                task.subtasks[1].status = TaskStatus.COMPLETE
                task.subtasks[1].progress = 100
                task.progress = 50
                await task_manager._save_batches()
                
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.ERROR
                task.subtasks[1].status = TaskStatus.ERROR
                print(f"Phase 2 Error Task {task.id}: {e}")

    await asyncio.gather(*[run_phase2(t) for t in active_tasks])
    
    # Filter again
    active_tasks = [t for t in tasks if t.status != TaskStatus.ERROR]
    
    # --- PHASE 3: GENERATE IMAGES ---
    # Concurrency: 2 (Rate limits often stricter here)
    print(f"=== STARTING PHASE 3: IMAGES ({len(active_tasks)} tasks) ===")
    sem_phase3 = asyncio.Semaphore(2)
    
    async def run_phase3(task: Task):
        async with sem_phase3:
            try:
                task.current_subtask_index = 2
                task.subtasks[2].status = TaskStatus.RUNNING
                task.subtasks[2].message = "Generating avatar..."
                task.status = TaskStatus.GENERATING_IMAGE
                await task_manager._save_batches()
                
                p = task.profile_data or {}
                
                image_path, used_prompt = await generate_avatar(
                    gender=p.get('gender', task.gender),
                    ethnicity=p.get('ethnicity', task.ethnicity),
                    age_range=task.age_range,
                    origin=p.get('origin', task.origin),
                    model=image_model,
                    filename=f"{task.id}_avatar.jpg"
                )
                
                task.image_path = image_path
                
                try:
                    path = PROMPTS_DIR / f"{task.id}_image_prompt.txt"
                    with open(path, "w", encoding="utf-8") as f: f.write(used_prompt)
                except: pass
                
                task.subtasks[2].status = TaskStatus.COMPLETE
                task.subtasks[2].progress = 100
                task.progress = 80
                await task_manager._save_batches()
                
            except Exception as e:
                # KREA FALLBACK: If API fails, use mock avatar so we don't block the whole CV
                print(f"WARNING: Phase 3 (Krea) failed for Task {task.id}: {e}")
                print("FALLBACK: generating mock avatar instead...")
                
                try:
                    # Import internal mock function dynamically or assume it's available
                    from ..services.krea_service import _generate_mock_avatar
                    
                    mock_path = await _generate_mock_avatar(
                        gender=p.get('gender', task.gender),
                        ethnicity=p.get('ethnicity', task.ethnicity)
                    )
                    
                    task.image_path = mock_path
                    task.subtasks[2].status = TaskStatus.COMPLETE
                    task.subtasks[2].progress = 100
                    # Show the original error in the message so user knows why fallback happened
                    short_error = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
                    task.subtasks[2].message = f"Fallback Mode. Error: {short_error}"
                    # Also set the error field but keep status generally valid (or maybe Warning?)
                    task.error = f"Krea Error (Handled): {e}" 
                    
                    task.progress = 80
                    await task_manager._save_batches()
                    
                except Exception as fallback_e:
                    # If even fallback fails, then fail the task
                    task.error = f"Image Gen Failed: {e} | Fallback Failed: {fallback_e}"
                    task.status = TaskStatus.ERROR
                    task.subtasks[2].status = TaskStatus.ERROR
                    print(f"CRITICAL: Phase 3 completely failed Task {task.id}: {fallback_e}")

    await asyncio.gather(*[run_phase3(t) for t in active_tasks])
    
    # Filter again
    active_tasks = [t for t in tasks if t.status != TaskStatus.ERROR]

    # --- PHASE 4: HTML ASSEMBLY ---
    print(f"=== STARTING PHASE 4: HTML ASSEMBLY ({len(active_tasks)} tasks) ===")
    
    for task in active_tasks:
        try:
            # --- Phase 4: HTML Assembly ---
            task.current_subtask_index = 3
            task.subtasks[3].status = TaskStatus.RUNNING
            task.subtasks[3].message = "Assembling HTML..."
            await task_manager._save_batches()
            
            p = task.profile_data or {}
            
            # Format Filename
            safe_name = p.get("name", "CV").replace(" ", "_")
            safe_name = "".join([c for c in safe_name if c.isalnum() or c in ('_','-')])
            safe_role = p.get("role", "Role").replace(" ", "_").replace("/", "-")
            safe_role = "".join([c for c in safe_role if c.isalnum() or c in ('_','-')])
            
            filename = f"{task.id[:8]}_{safe_name}_{safe_role}.html"
            
            # Phase 4: Generate HTML (handled inside render_cv_pdf)
            # Phase 5: Generate PDF (also handled inside render_cv_pdf, but with image compression)
            
            # Mark Phase 4 as running
            task.subtasks[3].progress = 50
            task.subtasks[3].message = "Rendering HTML template..."
            await task_manager._save_batches()
            
            # Generate HTML and PDF (returns tuple)
            html_path, pdf_path = await render_cv_pdf(task.cv_data, task.image_path, filename)
            
            task.html_path = html_path
            
            # Mark Phase 4 (HTML) complete
            task.subtasks[3].status = TaskStatus.COMPLETE
            task.subtasks[3].progress = 100
            task.subtasks[3].message = "HTML generated"
            
            # --- Phase 5: PDF Generation ---
            task.current_subtask_index = 4
            task.subtasks[4].status = TaskStatus.RUNNING
            task.subtasks[4].progress = 50
            task.subtasks[4].message = "Generating PDF with selectable text..."
            await task_manager._save_batches()
            
            # Strict Verification: Check if PDF was actually created
            if pdf_path and pdf_path.endswith('.pdf') and Path(pdf_path).exists() and Path(pdf_path).stat().st_size > 0:
                task.pdf_path = pdf_path
                task.subtasks[4].status = TaskStatus.COMPLETE
                task.subtasks[4].progress = 100
                task.subtasks[4].message = "PDF Ready"
            else:
                # PDF Generation Failed
                task.pdf_path = None # Do not link missing file
                task.subtasks[4].status = TaskStatus.ERROR
                error_msg = f"PDF Generation Failed: File not created at {pdf_path}"
                task.subtasks[4].message = error_msg
                task.error = error_msg  # Set main task error so it shows in UI
                print(f"ERROR: {error_msg}")
                # We do NOT fail the whole task, just Phase 5 runs in ERROR state
            
            task.status = TaskStatus.COMPLETE
            task.progress = 100
            task.message = "Complete"
            await task_manager._save_batches()
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.ERROR
            print(f"Phase 4/5 Error Task {task.id}: {e}")
            import traceback
            traceback.print_exc()


@router.get("/models", response_model=ModelsResponse)
async def get_available_models():
    """Get all available LLM and image generation models."""
    return ModelsResponse(
        llm_models=get_llm_models(),
        image_models=get_image_models()
    )


@router.post("/generate", response_model=GenerationResponse)
async def start_generation(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Start a batch CV generation."""
    # Create batch
    batch = await task_manager.create_batch(
        qty=request.qty,
        genders=request.genders,
        ethnicities=request.ethnicities,
        origins=request.origins,
        roles=request.roles,
        age_min=request.age_min,
        age_max=request.age_max,
        expertise_levels=request.expertise_levels,
        remote=request.remote
    )
    
    # Store model selections
    batch_models[batch.id] = {
        "profile_model": request.profile_model or request.llm_model,
        "cv_model": request.cv_model or request.llm_model,
        "image_model": request.image_model
    }
    
    # Start background processing
    background_tasks.add_task(
        process_batch, 
        batch.id, 
        request.profile_model or request.llm_model, # Phase 1
        request.cv_model or request.llm_model,      # Phase 2
        request.image_model
    )
    
    return GenerationResponse(
        batch_id=batch.id,
        message=f"Started generation of {request.qty} CVs",
        total_tasks=len(batch.tasks)
    )


@router.get("/status")
async def get_status():
    """Get the current batch generation status."""
    batch = task_manager.get_current_batch()
    
    if not batch:
        return JSONResponse(content={
            "batch_id": None,
            "total": 0,
            "completed": 0,
            "failed": 0,
            "in_progress": 0,
            "is_complete": True,
            "tasks": []
        })
    
    result = batch.to_dict()
    if batch.id in batch_models:
        result["models"] = batch_models[batch.id]
    
    return JSONResponse(content=result)


@router.get("/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status for a specific batch."""
    batch = task_manager.get_batch(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return JSONResponse(content=batch.to_dict())


@router.get("/files", response_model=FilesResponse)
async def list_files():
    """List all generated files (PDF and HTML)."""
    files = []
    if OUTPUT_DIR.exists():
        for pattern in ["*.pdf", "*.html"]:
            for filepath in sorted(HTML_DIR.glob(pattern), key=lambda x: x.stat().st_mtime, reverse=True):
                stat = filepath.stat()
                files.append(FileInfo(
                    filename=filepath.name,
                    path=str(filepath),
                    created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    size_kb=round(stat.st_size / 1024, 2)
                ))
    return FilesResponse(files=files, total=len(files))


@router.get("/files/{filename}")
async def get_file(filename: str):
    """Download/view a specific file."""
    filepath = HTML_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    media_type = "text/html" if filename.endswith('.html') else "application/pdf"
    return FileResponse(path=str(filepath), media_type=media_type, filename=filename)


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a file."""
    filepath = HTML_DIR / filename
    if filepath.exists():
        filepath.unlink()
    return {"message": f"Deleted {filename}"}


@router.post("/open-folder")
async def open_folder():
    """Open output folder."""
    # Modified to open the HTML directory as requested
    folder_path = str(HTML_DIR.absolute())
    try:
        if sys.platform == "win32":
            os.startfile(folder_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder_path])
        else:
            subprocess.run(["xdg-open", folder_path])
        return {"message": "Opened folder", "path": folder_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """Delete a specific task by ID."""
    success = task_manager.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": f"Task {task_id} deleted"}

@router.delete("/clear")
async def clear_all():
    """Clear all files."""
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.glob("*.*"):
            if f.is_file(): f.unlink()
    if HTML_DIR.exists():
        for f in HTML_DIR.glob("*.html"):
            f.unlink()
    if ASSETS_DIR.exists():
        for f in ASSETS_DIR.glob("avatar_*.jpg"):
            f.unlink()
    
    task_manager.clear_batches()
    batch_models.clear()
    return {"message": "Cleared all generated files"}


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "openrouter": bool(os.getenv("OPENROUTER_API_KEY")),
        "krea": bool(os.getenv("KREA_API_KEY"))
    }


@router.post("/regenerate-pdf/{html_filename}")
async def regenerate_pdf(html_filename: str):
    """
    Regenerate PDF from an existing HTML file.
    Creates a PDF with selectable text using Playwright.
    """
    try:
        pdf_path = await generate_pdf_from_existing_html(html_filename)
        pdf_filename = Path(pdf_path).name
        return {
            "success": True,
            "pdf_filename": pdf_filename,
            "pdf_url": f"/pdf/{pdf_filename}",
            "message": "PDF generated with selectable text"
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/regenerate-all-pdfs")
async def regenerate_all_pdfs(background_tasks: BackgroundTasks):
    """
    Regenerate PDFs for ALL existing HTML files.
    Runs in background due to potentially long processing time.
    """
    html_files = list((OUTPUT_DIR / "html").glob("*.html"))
    
    async def process_all():
        success = 0
        failed = 0
        for html_file in html_files:
            try:
                await generate_pdf_from_existing_html(html_file.name)
                success += 1
            except Exception as e:
                print(f"Failed to generate PDF for {html_file.name}: {e}")
                failed += 1
        print(f"Batch PDF regeneration complete: {success} success, {failed} failed")
    
    background_tasks.add_task(lambda: asyncio.run(process_all()))
    
    return {
        "message": f"Started regenerating PDFs for {len(html_files)} HTML files",
        "count": len(html_files)
    }
