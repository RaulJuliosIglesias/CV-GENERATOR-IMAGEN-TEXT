"""
Generation Router - API Endpoints for CV Generation
Handles batch generation, status tracking, and file management
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
from ..core.pdf_engine import render_cv_pdf
from ..services.llm_service import generate_cv_content
from ..services.nano_banana import generate_avatar, get_placeholder_avatar

# Get paths
BACKEND_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BACKEND_DIR / "output"
ASSETS_DIR = BACKEND_DIR / "assets"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

router = APIRouter(prefix="/api", tags=["generation"])


# Request/Response Models
class GenerationRequest(BaseModel):
    qty: int = Field(ge=1, le=20, default=1)
    gender: str = Field(default="any")
    ethnicity: str = Field(default="any")
    origin: str = Field(default="Europe")
    role: str = Field(default="Software Developer")


class GenerationResponse(BaseModel):
    batch_id: str
    message: str
    total_tasks: int


class StatusResponse(BaseModel):
    batch_id: str
    total: int
    completed: int
    failed: int
    in_progress: int
    is_complete: bool
    tasks: list


class FileInfo(BaseModel):
    filename: str
    path: str
    created_at: str
    size_kb: float


class FilesResponse(BaseModel):
    files: list[FileInfo]
    total: int


# Background task for generating a single CV
async def generate_single_cv(task: Task):
    """Generate a single CV with content and image."""
    try:
        # Step 1: Generate content and image concurrently
        await task_manager.update_task_status(
            task, TaskStatus.GENERATING_CONTENT, 
            "Generating CV content with AI...", 25
        )
        
        # Run both concurrently
        content_task = generate_cv_content(
            role=task.role,
            origin=task.origin,
            gender=task.gender
        )
        
        await task_manager.update_task_status(
            task, TaskStatus.GENERATING_IMAGE,
            "Generating avatar image...", 50
        )
        
        image_task = generate_avatar(
            gender=task.gender,
            ethnicity=task.ethnicity,
            age_range="25-45",
            origin=task.origin
        )
        
        # Wait for both to complete
        cv_data, image_path = await asyncio.gather(content_task, image_task)
        
        task.cv_data = cv_data
        task.image_path = image_path
        
        # Step 2: Render PDF
        await task_manager.update_task_status(
            task, TaskStatus.RENDERING_PDF,
            "Rendering PDF document...", 75
        )
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = cv_data.get("name", "CV").replace(" ", "_")
        filename = f"CV_{safe_name}_{task.id}_{timestamp}.pdf"
        
        # Render the PDF
        pdf_path = render_cv_pdf(cv_data, image_path, filename)
        task.pdf_path = pdf_path
        
        # Complete!
        await task_manager.update_task_status(
            task, TaskStatus.COMPLETE,
            "CV generated successfully!", 100
        )
        
    except Exception as e:
        await task_manager.set_task_error(task, str(e))
        print(f"Error generating CV {task.id}: {e}")


# Background task for processing a batch
async def process_batch(batch_id: str):
    """Process all tasks in a batch concurrently."""
    batch = task_manager.get_batch(batch_id)
    if not batch:
        return
    
    # Process all tasks concurrently (with some throttling to avoid overload)
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent generations
    
    async def process_with_semaphore(task: Task):
        async with semaphore:
            await generate_single_cv(task)
    
    await asyncio.gather(*[process_with_semaphore(t) for t in batch.tasks])


@router.post("/generate", response_model=GenerationResponse)
async def start_generation(request: GenerationRequest, background_tasks: BackgroundTasks):
    """
    Start a batch CV generation.
    
    Creates the specified number of CV generation tasks and processes them
    in the background. Use GET /status to track progress.
    """
    # Create batch
    batch = await task_manager.create_batch(
        qty=request.qty,
        gender=request.gender,
        ethnicity=request.ethnicity,
        origin=request.origin,
        role=request.role
    )
    
    # Start background processing
    background_tasks.add_task(process_batch, batch.id)
    
    return GenerationResponse(
        batch_id=batch.id,
        message=f"Started generation of {request.qty} CVs",
        total_tasks=len(batch.tasks)
    )


@router.get("/status")
async def get_status():
    """
    Get the current batch generation status.
    
    Returns detailed status for each CV in the current batch.
    """
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
    
    return JSONResponse(content=batch.to_dict())


@router.get("/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status for a specific batch."""
    batch = task_manager.get_batch(batch_id)
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return JSONResponse(content=batch.to_dict())


@router.get("/files", response_model=FilesResponse)
async def list_files():
    """
    List all generated PDF files.
    
    Returns a list of all PDF files in the output directory with metadata.
    """
    files = []
    
    if OUTPUT_DIR.exists():
        for filepath in sorted(OUTPUT_DIR.glob("*.pdf"), key=lambda x: x.stat().st_mtime, reverse=True):
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
    """Download a specific PDF file."""
    filepath = OUTPUT_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(filepath),
        media_type="application/pdf",
        filename=filename
    )


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """Delete a specific PDF file."""
    filepath = OUTPUT_DIR / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    filepath.unlink()
    return {"message": f"Deleted {filename}"}


@router.post("/open-folder")
async def open_folder():
    """
    Open the output directory in the OS file explorer.
    
    Works on Windows, macOS, and Linux.
    """
    folder_path = str(OUTPUT_DIR.absolute())
    
    try:
        if sys.platform == "win32":
            os.startfile(folder_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", folder_path])
        else:  # Linux
            subprocess.run(["xdg-open", folder_path])
        
        return {"message": "Opened folder", "path": folder_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not open folder: {str(e)}")


@router.delete("/clear")
async def clear_all():
    """Clear all generated files and batches."""
    # Clear files
    if OUTPUT_DIR.exists():
        for f in OUTPUT_DIR.glob("*.pdf"):
            f.unlink()
    
    if ASSETS_DIR.exists():
        for f in ASSETS_DIR.glob("avatar_*.jpg"):
            f.unlink()
    
    # Clear batches
    task_manager.clear_batches()
    
    return {"message": "Cleared all generated files and batches"}


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
