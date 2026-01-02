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
from ..core.pdf_engine import render_cv_html
from ..services.llm_service import generate_cv_content, get_available_models as get_llm_models, create_user_prompt
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
    llm_model: Optional[str] = Field(default=None, description="OpenRouter model ID")
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


# Background task for generating a single CV
async def generate_single_cv(task: Task, llm_model: Optional[str], image_model: Optional[str]):
    """Generate a single CV with sequential subtasks."""
    try:
        task.status = TaskStatus.GENERATING_CONTENT
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # --- SUBTASK 1: Drafting Prompts ---
        task.current_subtask_index = 0
        task.subtasks[0].status = TaskStatus.RUNNING
        task.subtasks[0].message = "Generating and saving prompt artifacts..."
        await task_manager._save_batches()
        
        # Safe age extraction (moved up for prompt gen)
        try:
            age = int(task.age_range.split('-')[0]) if '-' in task.age_range else int(task.age_range)
        except:
            age = 30

        try:
            # Generate Real Prompts
            cv_prompt = create_user_prompt(
                role=task.role,
                expertise=task.expertise,
                age=age,
                gender=task.gender,
                ethnicity=task.ethnicity,
                origin=task.origin,
                remote=task.remote
            )
            
            img_prompt = get_avatar_prompt(
                gender=task.gender,
                ethnicity=task.ethnicity,
                age_range=task.age_range
            )
            
            # Save prompts to organized prompts/ folder
            # Save prompts to organized prompts/ folder with ID-first naming
            p_cv_path = PROMPTS_DIR / f"{task.id}_cv_prompt.txt"
            p_img_path = PROMPTS_DIR / f"{task.id}_image_prompt.txt"
            
            with open(p_cv_path, "w", encoding="utf-8") as f:
                f.write(cv_prompt)
            with open(p_img_path, "w", encoding="utf-8") as f:
                f.write(img_prompt)

            task.subtasks[0].message = "Prompts exported to output folder"
            await task_manager._save_batches()
            await asyncio.sleep(1) 
            
        except Exception as e:
            print(f"Warning saving prompts: {e}")
        
        task.subtasks[0].status = TaskStatus.COMPLETE
        task.subtasks[0].progress = 100
        task.progress = 10
        
        # --- SUBTASK 2: Generating Content (LLM) ---
        task.current_subtask_index = 1
        task.subtasks[1].status = TaskStatus.RUNNING
        task.subtasks[1].message = f"Generating premium content ({llm_model or 'Auto'})..."
        await task_manager._save_batches()

        # Age already extracted above

        cv_data = await generate_cv_content(
            role=task.role,
            expertise=task.expertise,
            age=age,
            gender=task.gender,
            ethnicity=task.ethnicity,
            origin=task.origin,
            remote=task.remote,
            model=llm_model
        )
        task.cv_data = cv_data
        
        task.subtasks[1].status = TaskStatus.COMPLETE
        task.subtasks[1].progress = 100
        task.progress = 40
        
        # --- SUBTASK 3: Generating Visuals (AI) ---
        task.current_subtask_index = 2
        task.subtasks[2].status = TaskStatus.RUNNING
        task.subtasks[2].message = "Designing professional avatar..."
        await task_manager._save_batches()

        # Resolve gender coherence: Use LLM generated gender if available (e.g. for "Any")
        effective_gender = task.gender
        if cv_data and isinstance(cv_data, dict):
            # Try meta field
            meta_gender = cv_data.get("meta", {}).get("generated_gender")
            if meta_gender:
                effective_gender = meta_gender
                print(f"DEBUG: Using gender from LLM meta: {effective_gender}")

        image_path = await generate_avatar(
            gender=effective_gender,
            ethnicity=task.ethnicity,
            age_range=task.age_range,
            origin=task.origin,
            model=image_model,
            filename=f"{task.id}_avatar.jpg"
        )
        task.image_path = image_path
        
        task.subtasks[2].status = TaskStatus.COMPLETE
        task.subtasks[2].progress = 100
        task.progress = 70
        
        # --- SUBTASK 4: Assembling HTML ---
        task.current_subtask_index = 3
        task.subtasks[3].status = TaskStatus.RUNNING
        task.subtasks[3].message = "Assembling LeaG76 Template..."
        await task_manager._save_batches()
        
        # Clean and format filename: Name_Role_Expertise_ID.html
        safe_name = cv_data.get("name", "CV").replace(" ", "_")
        safe_name = "".join([c for c in safe_name if c.isalnum() or c in ('_','-')])
        
        safe_role = task.role.replace(" ", "_") if task.role != "any" else cv_data.get("title", "Role").replace(" ", "_")
        safe_role = "".join([c for c in safe_role if c.isalnum() or c in ('_','-')])
        
        safe_expertise = task.expertise
        
        # Format: ID_Name_Role.html -> ID first for sorting
        filename = f"{task.id[:8]}_{safe_name}_{safe_role}_{safe_expertise}.html"
        
        html_path = await render_cv_html(cv_data, image_path, filename, HTML_DIR)
        task.html_path = html_path
        
        task.subtasks[3].status = TaskStatus.COMPLETE
        task.subtasks[3].progress = 100
        task.progress = 90
        
        # --- SUBTASK 5: Finalizing & Exporting ---
        task.current_subtask_index = 4
        task.subtasks[4].status = TaskStatus.RUNNING
        task.subtasks[4].message = "Finalizing export..."
        await task_manager._save_batches()
        
        task.pdf_path = html_path # Points to HTML for client export
        
        task.subtasks[4].status = TaskStatus.COMPLETE
        task.subtasks[4].progress = 100
        task.progress = 100
        
        # COMPLETE
        task.status = TaskStatus.COMPLETE
        task.message = "CV Generated Successfully"
        await task_manager._save_batches()
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error generating CV {task.id}: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Mark current subtask as failed
        if task.current_subtask_index < len(task.subtasks):
            task.subtasks[task.current_subtask_index].status = TaskStatus.ERROR
            task.subtasks[task.current_subtask_index].message = error_msg
            
        task.status = TaskStatus.ERROR
        task.error = error_msg
        await task_manager._save_batches()


# Background task for processing a batch
async def process_batch(batch_id: str, llm_model: Optional[str], image_model: Optional[str]):
    """Process all tasks in a batch concurrently."""
    batch = task_manager.get_batch(batch_id)
    if not batch:
        return
    
    # Process all tasks concurrently (max 3)
    semaphore = asyncio.Semaphore(3)
    
    async def process_with_semaphore(task: Task):
        async with semaphore:
            await generate_single_cv(task, llm_model, image_model)
    
    await asyncio.gather(*[process_with_semaphore(t) for t in batch.tasks])


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
        "llm_model": request.llm_model,
        "image_model": request.image_model
    }
    
    # Start background processing
    background_tasks.add_task(
        process_batch, 
        batch.id, 
        request.llm_model, 
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
            for filepath in sorted(OUTPUT_DIR.glob(pattern), key=lambda x: x.stat().st_mtime, reverse=True):
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
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    media_type = "text/html" if filename.endswith('.html') else "application/pdf"
    return FileResponse(path=str(filepath), media_type=media_type, filename=filename)


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a file."""
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        filepath.unlink()
    return {"message": f"Deleted {filename}"}


@router.post("/open-folder")
async def open_folder():
    """Open output folder."""
    folder_path = str(OUTPUT_DIR.absolute())
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


@router.delete("/clear")
async def clear_all():
    """Clear all files."""
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.glob("*.*"):
            if f.is_file(): f.unlink()
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
