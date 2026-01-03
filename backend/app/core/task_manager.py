"""
Task Manager - Async queue manager for batch CV generation
Handles concurrent generation of multiple CVs with status tracking
"""

import asyncio
import uuid
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from pathlib import Path

# Import roles from the database service
from ..services.roles_service import get_all_roles, get_random_role, get_roles_by_expertise

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    GENERATING_CONTENT = "generating_content"
    GENERATING_IMAGE = "generating_image" 
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class Subtask:
    id: str
    name: str  # generate_text, generate_image, assemble_html, create_pdf
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0
    message: str = ""

@dataclass
class Task:
    id: str
    status: TaskStatus
    created_at: str
    role: str
    origin: str
    gender: str = "any"
    ethnicity: str = "any"
    batch_id: Optional[str] = None
    age_range: str = "25-35"
    expertise: str = "mid"
    remote: bool = False
    
    # Results
    profile_data: Optional[dict] = None # Phase 1 Result
    cv_data: Optional[dict] = None
    image_path: Optional[str] = None
    pdf_path: Optional[str] = None
    html_path: Optional[str] = None
    error: Optional[str] = None
    progress: int = 0
    message: str = "Initialized"
    
    # Subtasks tracking - PHASED PIPELINE
    subtasks: list[Subtask] = field(default_factory=lambda: [
        Subtask(id="1", name="Phase 1: Generating Unique Profile"),
        Subtask(id="2", name="Phase 2: Generating CV Content"),
        Subtask(id="3", name="Phase 3: Generating Visuals"),
        Subtask(id="4", name="Phase 4: Assembly & HTML"),
        Subtask(id="5", name="Phase 5: PDF Generation")
    ])
    current_subtask_index: int = 0

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status.value,
            "created_at": self.created_at,
            "role": self.role,
            "origin": self.origin,
            "gender": self.gender,
            "ethnicity": self.ethnicity,
            "batch_id": self.batch_id,
            "age_range": self.age_range,
            "expertise": self.expertise,
            "remote": self.remote,
            "progress": self.progress,
            "message": self.message,
            "pdf_path": f"/api/files/{Path(self.pdf_path).name}" if self.pdf_path else None,
            "html_path": f"/api/files/{Path(self.html_path).name}" if self.html_path else None,
            "image_path": f"/assets/{Path(self.image_path).name}" if self.image_path else None,
            "error": self.error,
            "subtasks": [
                {
                    "id": s.id,
                    "name": s.name,
                    "status": s.status.value,
                    "progress": s.progress,
                    "message": s.message
                } for s in self.subtasks
            ]
        }


@dataclass
class Batch:
    """Represents a batch of CV generation tasks."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tasks: list[Task] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def total(self) -> int:
        return len(self.tasks)
    
    @property
    def completed(self) -> int:
        return sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETE)
    
    @property
    def failed(self) -> int:
        return sum(1 for t in self.tasks if t.status == TaskStatus.ERROR)
    
    @property
    def in_progress(self) -> int:
        return sum(1 for t in self.tasks if t.status not in [TaskStatus.PENDING, TaskStatus.COMPLETE, TaskStatus.ERROR])
    
    @property
    def is_complete(self) -> bool:
        return all(t.status in [TaskStatus.COMPLETE, TaskStatus.ERROR] for t in self.tasks)
    
    def to_dict(self) -> dict:
        """Convert batch to dictionary for API response."""
        return {
            "id": self.id,
            "total": self.total,
            "completed": self.completed,
            "failed": self.failed,
            "in_progress": self.in_progress,
            "is_complete": self.is_complete,
            "created_at": self.created_at.isoformat(),
            "tasks": [t.to_dict() for t in self.tasks]
        }


# Pools for randomization when "any" is selected - loaded from database
from ..services.roles_service import get_gender_values, get_ethnicity_values, get_origin_values

def _get_genders_pool() -> list[str]:
    """Get genders from database with fallback."""
    try:
        genders = get_gender_values()
        if genders:
            return genders
    except Exception as e:
        print(f"WARNING: Failed to load genders from db: {e}")
    return ["Male", "Female"]

def _get_ethnicities_pool() -> list[str]:
    """Get ethnicities from database with fallback."""
    try:
        ethnicities = get_ethnicity_values()
        if ethnicities:
            return ethnicities
    except Exception as e:
        print(f"WARNING: Failed to load ethnicities from db: {e}")
    return ["Asian", "Black", "White", "Hispanic"]

def _get_origins_pool() -> list[str]:
    """Get origins from database with fallback."""
    try:
        origins = get_origin_values()
        if origins:
            return origins
    except Exception as e:
        print(f"WARNING: Failed to load origins from db: {e}")
    return ["United States", "United Kingdom", "Germany"]

# Load roles dynamically from the database
def _get_roles_pool() -> list[str]:
    """Get all roles from the database, with fallback."""
    try:
        roles = get_all_roles()
        if roles:
            return roles
    except Exception as e:
        print(f"WARNING: Failed to load roles from database: {e}")
    
    # Fallback if database fails
    return ["Software Engineer", "Product Manager", "UX Designer", "Data Scientist"]

class TaskManager:
    """
    Manages CV generation tasks and batches.
    Handles concurrent execution and status tracking.
    """
    
    def __init__(self):
        self.batches: dict[str, Batch] = {}
        self.current_batch_id: Optional[str] = None
        self._lock = asyncio.Lock()
    
    async def create_batch(
        self,
        qty: int,
        genders: list[str],
        ethnicities: list[str],
        origins: list[str],
        roles: list[str],
        age_min: int,
        age_max: int,
        expertise_levels: list[str],
        remote: bool = False
    ) -> Batch:
        """Create a new batch of CV generation tasks."""
        
        batch_id = str(uuid.uuid4())[:8]
        tasks = []
        
        for i in range(qty):
            task_id = str(uuid.uuid4())[:8]
            
            # --- CRITICAL: RESOLVE "ANY" TO CONCRETE VALUES HERE ---
            # This ensures that we pass a SPECIFIC profile to the LLM, 
            # preventing it from defaulting to "Rafael Mendoza" every time.
            
            # 1. Resolve Gender (from database)
            if not genders or "any" in [g.lower() for g in genders]:
                selected_gender = random.choice(_get_genders_pool())
            else:
                selected_gender = random.choice(genders)
                
            # 2. Resolve Ethnicity (from database)
            if not ethnicities or "any" in [e.lower() for e in ethnicities]:
                selected_ethnicity = random.choice(_get_ethnicities_pool())
            else:
                selected_ethnicity = random.choice(ethnicities)
                
            # 3. Resolve Origin (from database)
            if not origins or "any" in [o.lower() for o in origins]:
                selected_origin = random.choice(_get_origins_pool())
            else:
                selected_origin = random.choice(origins)
            
            # 4. Resolve Expertise FIRST (needed for coherent role selection)
            selected_expertise = random.choice(expertise_levels) if expertise_levels else "mid"
            
            # 5. Resolve Role - MUST match expertise level for coherence
            if not roles or "any" in [r.lower() for r in roles]:
                # Get roles appropriate for this expertise level
                expertise_roles = get_roles_by_expertise(selected_expertise)
                print(f"DEBUG BATCH: Expertise '{selected_expertise}' -> {len(expertise_roles)} roles available")
                if expertise_roles:
                    selected_role = random.choice(expertise_roles)
                else:
                    print(f"WARNING BATCH: No roles for expertise '{selected_expertise}', using fallback pool")
                    selected_role = random.choice(_get_roles_pool())
            else:
                selected_role = random.choice(roles)
            
            # Generate random age within the specified range
            selected_age = random.randint(age_min, age_max)
            age_range = f"{selected_age}"
            
            print(f"DEBUG BATCH: Task {task_id} -> Role: {selected_role}, Expertise: {selected_expertise}, "
                  f"Gender: {selected_gender}, Ethnicity: {selected_ethnicity}, Origin: {selected_origin}")

            task = Task(
                id=task_id,
                batch_id=batch_id,
                status=TaskStatus.PENDING,
                created_at=datetime.now().isoformat(),
                role=selected_role,
                origin=selected_origin,
                gender=selected_gender,
                ethnicity=selected_ethnicity,
                age_range=age_range,
                expertise=selected_expertise,
                remote=remote,
                message="Queued for generation",
                progress=0
            )
            tasks.append(task)
        
        batch = Batch(id=batch_id, tasks=tasks)
        self.batches[batch_id] = batch
        self.current_batch_id = batch_id
        
        return batch
    
    def get_batch(self, batch_id: str) -> Optional[Batch]:
        """Get a batch by ID."""
        return self.batches.get(batch_id)
    
    def get_current_batch(self) -> Optional[Batch]:
        """Get the current active batch."""
        if self.current_batch_id:
            return self.batches.get(self.current_batch_id)
        return None
    
    async def _save_batches(self):
        """Dummy persistent save - could implement JSON DB here."""
        pass
    
    def get_all_batches(self) -> list[Batch]:
        """Get all batches."""
        return list(self.batches.values())
    

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID from any batch."""
        for batch in self.batches.values():
            initial_len = len(batch.tasks)
            batch.tasks = [t for t in batch.tasks if t.id != task_id]
            if len(batch.tasks) < initial_len:
                # If we had persistence, we would save here
                self._save_batches() 
                return True
        return False

    def clear_batches(self):
        """Clear all completed batches."""
        self.batches = {
            k: v for k, v in self.batches.items()
            if not v.is_complete
        }


# Global task manager instance
task_manager = TaskManager()
