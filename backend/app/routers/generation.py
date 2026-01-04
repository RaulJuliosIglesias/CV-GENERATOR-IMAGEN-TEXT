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
from fastapi import APIRouter, HTTPException, BackgroundTasks, Header
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional

from ..core.task_manager import task_manager, Task, TaskStatus
from ..core.pdf_engine import render_cv_pdf, generate_pdf_from_existing_html
from ..services.llm_service import generate_cv_content_v2, generate_profile_data, get_available_models as get_llm_models, create_user_prompt
from ..services.krea_service import generate_avatar, get_available_models as get_image_models, get_avatar_prompt
import random

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BACKEND_DIR / "output"
ASSETS_DIR = BACKEND_DIR / "assets"

# Organized output subdirectories
PROMPTS_DIR = OUTPUT_DIR / "prompts"
HTML_DIR = OUTPUT_DIR / "html"
PDFS_DIR = OUTPUT_DIR / "pdf"  # Must match pdf_engine.py
AVATARS_DIR = OUTPUT_DIR / "avatars"

# Detect Vercel environment
IS_VERCEL = os.getenv('VERCEL') == '1' or os.getenv('VERCEL_ENV') is not None

# Ensure all directories exist (skip on Vercel - read-only filesystem)
if not IS_VERCEL:
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
    smart_category: bool = Field(default=False, description="Organize PDFs into category subfolders based on role")
    # New separate models
    profile_model: Optional[str] = Field(default=None, description="LLM for Profile Generation")
    cv_model: Optional[str] = Field(default=None, description="LLM for CV Content")
    # Legacy fallback
    llm_model: Optional[str] = Field(default=None, description="Fallback LLM model")
    image_model: Optional[str] = Field(default=None, description="Krea model ID")
    image_size: int = Field(default=100, ge=50, le=200, description="Profile image scale percentage")
    # API Keys are passed via Headers, but we could also accept them here if needed.
    # For now, we prefer Headers for security/standard practice.


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

@router.post("/generate", response_model=GenerationResponse)
async def start_generation(
    request: GenerationRequest, 
    background_tasks: BackgroundTasks,
    x_openrouter_key: Optional[str] = Header(None, alias="X-OpenRouter-Key"),
    x_krea_key: Optional[str] = Header(None, alias="X-Krea-Key")
):
    """Start a batch CV generation."""
    from ..services.batch_service import process_batch, batch_models
    
    # Collect API Keys
    api_keys = {
        "openrouter": x_openrouter_key,
        "krea": x_krea_key
    }
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
        request.image_model,
        request.smart_category,  # Smart Category mode
        request.image_size,      # Pass image_size here
        api_keys                 # Pass API keys
    )
    
    return GenerationResponse(
        batch_id=batch.id,
        message=f"Started generation of {request.qty} CVs",
        total_tasks=len(batch.tasks)
    )


@router.get("/status")
async def get_status():
    """Get the current batch generation status."""
    from ..services.batch_service import batch_models
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
    """List generated CVs - one entry per CV (HTML files only, frontend derives PDF)."""
    files = []
    
    # Only list HTML files - each HTML represents one CV
    # Frontend will use the filename to construct PDF URL
    if HTML_DIR.exists():
        for filepath in sorted(HTML_DIR.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
            stat = filepath.stat()
            files.append(FileInfo(
                filename=filepath.name,
                path=str(filepath),
                created_at=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                size_kb=round(stat.st_size / 1024, 2)
            ))
    
    return FilesResponse(files=files, total=len(files))


@router.get("/files/html/{filename}")
async def get_html_file(filename: str):
    """Download/view a specific HTML file."""
    filepath = HTML_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="HTML File not found")
    return FileResponse(path=str(filepath), media_type="text/html")  # No filename = opens inline


@router.get("/files/pdf/{filename}")
async def get_pdf_file(filename: str):
    """Download/view a specific PDF file."""
    filepath = PDFS_DIR / filename
    
    # 1. Check root PDF dir (Legacy/Normal)
    if filepath.exists():
        return FileResponse(path=str(filepath), media_type="application/pdf")
        
    # 2. Smart Category Support: Search in subdirectories
    # We use rglob to find the file in any category subfolder
    found_files = list(PDFS_DIR.rglob(filename))
    if found_files:
        return FileResponse(path=str(found_files[0]), media_type="application/pdf")

    raise HTTPException(status_code=404, detail="PDF File not found")


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a file (HTML and its corresponding PDF)."""
    deleted = []
    
    # 1. Delete HTML
    html_path = HTML_DIR / filename
    if html_path.exists():
        html_path.unlink()
        deleted.append("HTML")
        
    # 2. Delete PDF (Check root and subfolders)
    pdf_filename = filename.replace('.html', '.pdf')
    pdf_path = PDFS_DIR / pdf_filename
    
    if pdf_path.exists():
        pdf_path.unlink()
        deleted.append("PDF")
    else:
        # Search in subfolders
        found_pdfs = list(PDFS_DIR.rglob(pdf_filename))
        for p in found_pdfs:
            p.unlink()
            deleted.append(f"PDF({p.parent.name})")
            
    if not deleted:
         # If nothing found, still return success to keep frontend in sync
         return {"message": "File not found but cleared"}
         
    return {"message": f"Deleted {' + '.join(deleted)}"}


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
