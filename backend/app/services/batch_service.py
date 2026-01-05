"""
Batch Generation Service - OPTIMIZED
Handles the heavy lifting of the generation pipeline:
- Profile Generation (Phase 1)
- CV Content Generation (Phase 2) ← PARALLELIZED
- Image Generation (Phase 3) ← PARALLELIZED with Phase 2
- HTML & PDF Rendering (Phase 4+5)

Performance optimizations:
- Phase 2 and 3 run in parallel (both only depend on Phase 1)
- Increased semaphore for better concurrency
- Timing logs for debugging
"""

import asyncio
import os
import time
from pathlib import Path
from typing import Optional

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
    Execute the OPTIMIZED PIPELINED Generation Pipeline.
    
    OPTIMIZATION: Phase 2 (CV Content) and Phase 3 (Image) now run in PARALLEL
    since they both only depend on Phase 1 data.
    
    Args:
        smart_category: If True, organize PDFs into category subfolders based on role
    """
    batch = task_manager.get_batch(batch_id)
    if not batch: return
    
    tasks = batch.tasks
    batch_start = time.time()
    
    # OPTIMIZED: Increased from 5 to 10 for better throughput
    # OpenRouter supports ~50 req/min, Krea supports concurrent jobs
    global_semaphore = asyncio.Semaphore(10)
    
    async def process_single_task(task: Task):
        """Process a single task through all 5 phases with optimized parallelization."""
        task_start = time.time()
        
        # ========== PHASE 1: PROFILE ==========
        phase1_start = time.time()
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
                
                phase1_time = time.time() - phase1_start
                print(f"⏱️ Task {task.id} Phase 1: {phase1_time:.1f}s")
                
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.ERROR
                task.subtasks[0].status = TaskStatus.ERROR
                print(f"Phase 1 Error Task {task.id}: {e}")
                return  # Stop this task, but don't affect others
        
        # ========== PHASE 2 + PHASE 3: PARALLEL EXECUTION ==========
        # These phases are INDEPENDENT - both only need profile_data from Phase 1
        phase2_3_start = time.time()
        
        p = task.profile_data or {}
        
        # Update UI to show both phases starting
        task.current_subtask_index = 1
        task.subtasks[1].status = TaskStatus.RUNNING
        task.subtasks[1].message = "Writing CV content..."
        task.subtasks[2].status = TaskStatus.RUNNING
        task.subtasks[2].message = "Generating avatar..."
        task.status = TaskStatus.GENERATING_CONTENT
        await task_manager._save_batches()
        
        async def phase2_cv_content():
            """Phase 2: Generate CV Content"""
            async with global_semaphore:
                try:
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
                    
                    # Save prompt for debugging
                    try:
                        if not PROMPTS_DIR.exists():
                            PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
                        path = PROMPTS_DIR / f"{task.id}_cv_prompt.txt"
                        with open(path, "w", encoding="utf-8") as f: 
                            f.write(used_prompt)
                    except: 
                        pass
                    
                    return cv_data, None
                    
                except Exception as e:
                    return None, str(e)
        
        async def phase3_image():
            """Phase 3: Generate Avatar Image"""
            async with global_semaphore:
                try:
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
                    
                    # Save prompt for debugging
                    try:
                        path = PROMPTS_DIR / f"{task.id}_image_prompt.txt"
                        with open(path, "w", encoding="utf-8") as f: 
                            f.write(used_prompt)
                    except: 
                        pass
                    
                    return image_path, None
                    
                except Exception as e:
                    return None, str(e)
        
        # RUN BOTH PHASES IN PARALLEL
        results = await asyncio.gather(
            phase2_cv_content(),
            phase3_image(),
            return_exceptions=True
        )
        
        phase2_3_time = time.time() - phase2_3_start
        print(f"⏱️ Task {task.id} Phase 2+3 (parallel): {phase2_3_time:.1f}s")
        
        # Process Phase 2 result
        cv_result = results[0]
        if isinstance(cv_result, Exception):
            task.error = str(cv_result)
            task.status = TaskStatus.ERROR
            task.subtasks[1].status = TaskStatus.ERROR
            print(f"Phase 2 Error Task {task.id}: {cv_result}")
            return
        
        cv_data, cv_error = cv_result
        if cv_error:
            task.error = cv_error
            task.status = TaskStatus.ERROR
            task.subtasks[1].status = TaskStatus.ERROR
            print(f"Phase 2 Error Task {task.id}: {cv_error}")
            return
        
        task.cv_data = cv_data
        task.subtasks[1].status = TaskStatus.COMPLETE
        task.subtasks[1].progress = 100
        task.progress = 50
        
        # Process Phase 3 result
        image_result = results[1]
        if isinstance(image_result, Exception):
            # Image failed - try fallback
            print(f"WARNING: Phase 3 (Krea) failed for Task {task.id}: {image_result}")
            try:
                from ..services.krea_service import _generate_mock_avatar
                mock_path = await _generate_mock_avatar(
                    gender=p.get('gender', task.gender),
                    ethnicity=p.get('ethnicity', task.ethnicity)
                )
                task.image_path = mock_path
                task.subtasks[2].status = TaskStatus.COMPLETE
                task.subtasks[2].progress = 100
                task.subtasks[2].message = "Fallback avatar used"
            except Exception as fallback_e:
                task.error = f"Image Gen Failed: {image_result} | Fallback Failed: {fallback_e}"
                task.status = TaskStatus.ERROR
                task.subtasks[2].status = TaskStatus.ERROR
                print(f"CRITICAL: Phase 3 completely failed Task {task.id}: {fallback_e}")
                return
        else:
            image_path, image_error = image_result
            if image_error:
                # Try fallback
                print(f"WARNING: Phase 3 error for Task {task.id}: {image_error}")
                try:
                    from ..services.krea_service import _generate_mock_avatar
                    mock_path = await _generate_mock_avatar(
                        gender=p.get('gender', task.gender),
                        ethnicity=p.get('ethnicity', task.ethnicity)
                    )
                    task.image_path = mock_path
                    task.subtasks[2].message = f"Fallback. Error: {image_error[:50]}..."
                except Exception as fallback_e:
                    task.error = f"Image Gen Failed: {image_error} | Fallback Failed: {fallback_e}"
                    task.status = TaskStatus.ERROR
                    task.subtasks[2].status = TaskStatus.ERROR
                    return
            else:
                task.image_path = image_path
        
        task.subtasks[2].status = TaskStatus.COMPLETE
        task.subtasks[2].progress = 100
        task.progress = 80
        await task_manager._save_batches()
        
        # ========== PHASE 4 & 5: HTML + PDF ==========
        phase4_5_start = time.time()
        try:
            task.current_subtask_index = 3
            task.subtasks[3].status = TaskStatus.RUNNING
            task.subtasks[3].message = "Assembling HTML..."
            await task_manager._save_batches()
            
            import random
            
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
            
            phase4_5_time = time.time() - phase4_5_start
            total_time = time.time() - task_start
            print(f"⏱️ Task {task.id} Phase 4+5: {phase4_5_time:.1f}s | TOTAL: {total_time:.1f}s")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.ERROR
            print(f"Phase 4/5 Error Task {task.id}: {e}")
            import traceback
            traceback.print_exc()
    
    # Launch ALL tasks concurrently - each runs through its full pipeline
    print(f"=== STARTING OPTIMIZED PIPELINED GENERATION ({len(tasks)} tasks, semaphore=10) ===")
    await asyncio.gather(*[process_single_task(t) for t in tasks])
    
    total_batch_time = time.time() - batch_start
    print(f"=== BATCH COMPLETE in {total_batch_time:.1f}s ({total_batch_time/len(tasks):.1f}s per CV) ===")
