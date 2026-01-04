"""
Batch Generation Service
Handles the heavy lifting of the generation pipeline:
- Profile Generation
- CV Content Generation
- Image Generation
- HTML & PDF Rendering

Refactored from generation.py to separate concerns.
"""

import asyncio
import os
from pathlib import Path
from typing import Optional
import random

from ..core.task_manager import task_manager, Task, TaskStatus
from ..core.pdf_engine import render_cv_pdf
from ..services.llm_service import generate_cv_content_v2, generate_profile_data
from ..services.krea_service import generate_avatar

# Get paths (same as in generation.py for consistency)
BACKEND_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BACKEND_DIR / "output"
PROMPTS_DIR = OUTPUT_DIR / "prompts"

# Store selected models per batch (moved from router)
batch_models = {}

async def process_batch(batch_id: str, profile_model: Optional[str], cv_model: Optional[str], image_model: Optional[str], smart_category: bool = False, image_size: int = 100, api_keys: dict = None):
    """
    Execute the PIPELINED Generation Pipeline.
    
    Args:
        smart_category: If True, organize PDFs into category subfolders based on role
    """
    batch = task_manager.get_batch(batch_id)
    if not batch: return
    
    tasks = batch.tasks
    
    # Global semaphore to limit total concurrent API calls (prevents rate limiting)
    global_semaphore = asyncio.Semaphore(5)
    
    async def process_single_task(task: Task):
        """Process a single task through all 5 phases."""
        
        # ========== PHASE 1: PROFILE ==========
        async with global_semaphore:
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
                    model=profile_model,
                    api_key=api_keys.get('openrouter') if api_keys else None
                )
                
                task.profile_data = profile_data
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
                return  # Stop this task, but don't affect others
        
        # ========== PHASE 2: CV CONTENT ==========
        async with global_semaphore:
            try:
                task.current_subtask_index = 1
                task.subtasks[1].status = TaskStatus.RUNNING
                task.subtasks[1].message = "Writing detailed CV..."
                task.status = TaskStatus.GENERATING_CONTENT
                await task_manager._save_batches()
                
                p = task.profile_data or {}
                
                cv_data, used_prompt = await generate_cv_content_v2(
                    role=p.get('role', task.role),
                    expertise=task.expertise,
                    age=p.get('age', 30),
                    gender=p.get('gender', task.gender),
                    ethnicity=p.get('ethnicity', task.ethnicity),
                    origin=p.get('origin', task.origin),
                    remote=task.remote,
                    model=cv_model,
                    name=p.get('name'),
                    profile_data=p,
                    api_key=api_keys.get('openrouter') if api_keys else None
                )
                
                task.cv_data = cv_data
                
                try:
                    if not PROMPTS_DIR.exists():
                        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
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
                return
        
        # ========== PHASE 3: IMAGE ==========
        async with global_semaphore:
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
                    age_range=str(p.get('age', task.age_range)),
                    origin=p.get('origin', task.origin),
                    role=p.get('role', task.role),
                    model=image_model,
                    filename=f"{task.id}_avatar.jpg",
                    api_key=api_keys.get('krea') if api_keys else None
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
                # KREA FALLBACK
                print(f"WARNING: Phase 3 (Krea) failed for Task {task.id}: {e}")
                try:
                    from ..services.krea_service import _generate_mock_avatar
                    p = task.profile_data or {}
                    mock_path = await _generate_mock_avatar(
                        gender=p.get('gender', task.gender),
                        ethnicity=p.get('ethnicity', task.ethnicity)
                    )
                    task.image_path = mock_path
                    task.subtasks[2].status = TaskStatus.COMPLETE
                    task.subtasks[2].progress = 100
                    short_error = str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
                    task.subtasks[2].message = f"Fallback Mode. Error: {short_error}"
                    task.error = f"Krea Error (Handled): {e}"
                    task.progress = 80
                    await task_manager._save_batches()
                except Exception as fallback_e:
                    task.error = f"Image Gen Failed: {e} | Fallback Failed: {fallback_e}"
                    task.status = TaskStatus.ERROR
                    task.subtasks[2].status = TaskStatus.ERROR
                    print(f"CRITICAL: Phase 3 completely failed Task {task.id}: {fallback_e}")
                    return
        
        # ========== PHASE 4 & 5: HTML + PDF ==========
        try:
            task.current_subtask_index = 3
            task.subtasks[3].status = TaskStatus.RUNNING
            task.subtasks[3].message = "Assembling HTML..."
            await task_manager._save_batches()
            
            p = task.profile_data or {}
            
            safe_name = p.get("name", "CV").replace(" ", "_")
            safe_name = "".join([c for c in safe_name if c.isalnum() or c in ('_','-')])
            safe_role = p.get("role", "Role").replace(" ", "_").replace("/", "-")
            safe_role = "".join([c for c in safe_role if c.isalnum() or c in ('_','-')])
            
            filename = f"{task.id[:8]}__{safe_name}__{safe_role}.html"
            
            task.subtasks[3].progress = 50
            task.subtasks[3].message = "Rendering HTML template..."
            await task_manager._save_batches()
            
            # Generate consistent sidebar color for both HTML and PDF
            sidebar_colors = [
                '#E3F2FD', '#D1EAED', '#D4E6F1', '#EBF5FB', # Blues
                '#E8F5E9', '#DCE6D9', '#EAFAF1',            # Greens
                '#FAF2D3', '#FDEBD0', '#E6DDCF',            # Warm
                '#F4ECF7', '#E8DAEF', '#FADBD8',            # Rose/Purple
                '#E5E7E9', '#EAEDED', '#F2F3F4', '#D7DBDD'  # Neutrals
            ]
            sidebar_color = random.choice(sidebar_colors)
            
            result = await render_cv_pdf(
                task.cv_data, 
                task.image_path, 
                filename,
                smart_category=smart_category,
                role=p.get("role", task.role),
                image_size=image_size,
                sidebar_color=sidebar_color
            )
            
            if result is None:
                raise RuntimeError("render_cv_pdf returned None - critical failure")
            
            html_path, pdf_path = result
            task.html_path = html_path
            
            task.subtasks[3].status = TaskStatus.COMPLETE
            task.subtasks[3].progress = 100
            task.subtasks[3].message = "HTML generated"
            
            # Phase 5: PDF
            task.current_subtask_index = 4
            task.subtasks[4].status = TaskStatus.RUNNING
            task.subtasks[4].progress = 50
            task.subtasks[4].message = "Generating PDF with selectable text..."
            await task_manager._save_batches()
            
            if pdf_path and pdf_path.endswith('.pdf') and Path(pdf_path).exists() and Path(pdf_path).stat().st_size > 0:
                task.pdf_path = pdf_path
                task.subtasks[4].status = TaskStatus.COMPLETE
                task.subtasks[4].progress = 100
                task.subtasks[4].message = "PDF Ready"
            else:
                task.pdf_path = None
                task.subtasks[4].status = TaskStatus.ERROR
                error_msg = f"PDF Generation Failed: File not created at {pdf_path}"
                task.subtasks[4].message = error_msg
                task.error = error_msg
                print(f"ERROR: {error_msg}")
            
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
    
    # Launch ALL tasks concurrently - each runs through its full pipeline
    print(f"=== STARTING PIPELINED GENERATION ({len(tasks)} tasks) ===")
    await asyncio.gather(*[process_single_task(t) for t in tasks])
    print(f"=== BATCH COMPLETE ===")
