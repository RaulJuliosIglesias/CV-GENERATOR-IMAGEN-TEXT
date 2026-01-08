"""
Generation Router - API Endpoints for CV Generation
Handles batch generation, status tracking, model selection, and file management
"""

import os
import asyncio
import subprocess
import sys
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Header
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List

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


@router.get("/models", response_model=ModelsResponse)
async def get_models():
    """Get available LLM and image models."""
    try:
        # Get LLM models (sync function, uses lazy-loaded cache)
        llm_models = get_llm_models()
        
        # Get image models from Krea service (also sync)
        image_models = get_image_models()
        
        print(f"DEBUG /api/models: Returning {len(llm_models)} LLM models, {len(image_models)} image models")
        
        return ModelsResponse(
            llm_models=llm_models,
            image_models=image_models
        )
    except Exception as e:
        print(f"Error fetching models: {e}")
        # Return empty lists on error so frontend doesn't break
        return ModelsResponse(
            llm_models=[],
            image_models=get_image_models()  # Image models are static
        )


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


class DownloadZipRequest(BaseModel):
    batch_ids: Optional[List[str]] = Field(default=None, description="List of batch IDs to include. If None, downloads all files.")
    filenames: Optional[List[str]] = Field(default=None, description="List of specific HTML filenames to download. Takes precedence over batch_ids.")
    include_html: bool = Field(default=False, description="Include HTML files in ZIP")
    include_avatars: bool = Field(default=False, description="Include avatar images in ZIP")


@router.post("/download-zip")
async def download_zip(request: DownloadZipRequest):
    """
    Download multiple CVs as a ZIP file.
    
    Options:
    - batch_ids: List of specific batch IDs to download (None = all files)
    - include_html: Include HTML files alongside PDFs
    - include_avatars: Include avatar images
    
    Returns a ZIP file with all requested files.
    """
    from ..core.task_manager import task_manager
    
    # Collect PDF files to include
    pdf_files = []
    html_files = []
    avatar_files = []
    
    # Priority 1: Specific filenames (most specific)
    if request.filenames:
        for filename in request.filenames:
            # Remove .html extension if present, add .pdf
            base_name = filename.replace('.html', '').replace('.pdf', '')
            pdf_filename = f"{base_name}.pdf"
            
            # Search for PDF in root and subdirectories
            pdf_path = PDFS_DIR / pdf_filename
            if pdf_path.exists():
                pdf_files.append(pdf_path)
            else:
                # Search in subdirectories (smart_category)
                found_pdfs = list(PDFS_DIR.rglob(pdf_filename))
                if found_pdfs:
                    pdf_files.append(found_pdfs[0])
            
            # Include HTML if requested
            if request.include_html:
                html_filename = filename.replace('.pdf', '.html')
                html_path = HTML_DIR / html_filename
                if html_path.exists():
                    html_files.append(html_path)
    
    # Priority 2: Batch IDs (if no specific filenames)
    elif request.batch_ids:
        # Collect files from specific batches
        for batch_id in request.batch_ids:
            batch = task_manager.get_batch(batch_id)
            if not batch:
                continue
            
            for task in batch.tasks:
                if task.status == TaskStatus.COMPLETE:
                    # Get PDF path
                    if task.pdf_path:
                        pdf_path = Path(task.pdf_path)
                        if pdf_path.exists():
                            pdf_files.append(pdf_path)
                    
                    # Get HTML path if requested
                    if request.include_html and task.html_path:
                        html_path = Path(task.html_path)
                        if html_path.exists():
                            html_files.append(html_path)
                    
                    # Get avatar path if requested
                    if request.include_avatars and task.image_path:
                        avatar_path = Path(task.image_path)
                        if avatar_path.exists():
                            avatar_files.append(avatar_path)
    
    # Priority 3: All files (if neither filenames nor batch_ids specified)
    else:
        # Download ALL files (all PDFs in output/pdf)
        if PDFS_DIR.exists():
            # Get all PDFs (including subdirectories for smart_category)
            pdf_files = list(PDFS_DIR.rglob("*.pdf"))
        
        if request.include_html and HTML_DIR.exists():
            html_files = list(HTML_DIR.glob("*.html"))
        
        if request.include_avatars and AVATARS_DIR.exists():
            avatar_files = list(AVATARS_DIR.glob("*.jpg")) + list(AVATARS_DIR.glob("*.png"))
    
    if not pdf_files and not html_files and not avatar_files:
        raise HTTPException(status_code=404, detail="No files found to download")
    
    # Create temporary ZIP file
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    temp_zip_path = Path(temp_zip.name)
    
    try:
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add PDFs
            for pdf_file in pdf_files:
                # Preserve folder structure for smart_category
                if pdf_file.parent != PDFS_DIR:
                    # File is in a subdirectory (category folder)
                    arcname = pdf_file.relative_to(PDFS_DIR)
                else:
                    # File is in root PDF directory
                    arcname = pdf_file.name
                zipf.write(pdf_file, arcname=f"PDFs/{arcname}")
            
            # Add HTMLs if requested
            if request.include_html:
                for html_file in html_files:
                    zipf.write(html_file, arcname=f"HTMLs/{html_file.name}")
            
            # Add avatars if requested
            if request.include_avatars:
                for avatar_file in avatar_files:
                    zipf.write(avatar_file, arcname=f"Avatars/{avatar_file.name}")
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"CVs_Batch_{timestamp}.zip"
        
        # Return ZIP as streaming response
        def cleanup():
            """Clean up temporary file after download."""
            try:
                if temp_zip_path.exists():
                    temp_zip_path.unlink()
            except Exception as e:
                print(f"Warning: Failed to cleanup temp ZIP: {e}")
        
        # Read ZIP file and stream it
        def generate():
            try:
                with open(temp_zip_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)  # 8KB chunks
                        if not chunk:
                            break
                        yield chunk
            finally:
                cleanup()
        
        return StreamingResponse(
            generate(),
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{zip_filename}"',
                "Content-Type": "application/zip"
            }
        )
        
    except Exception as e:
        # Cleanup on error
        if temp_zip_path.exists():
            temp_zip_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to create ZIP: {str(e)}")
