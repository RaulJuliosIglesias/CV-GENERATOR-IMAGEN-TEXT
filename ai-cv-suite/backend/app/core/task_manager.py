"""
Task Manager - Async queue manager for batch CV generation
Handles concurrent generation of multiple CVs with status tracking
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    GENERATING_CONTENT = "generating_content"
    GENERATING_IMAGE = "generating_image"
    RENDERING_PDF = "rendering_pdf"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class Task:
    """Represents a single CV generation task."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    batch_id: str = ""
    status: TaskStatus = TaskStatus.PENDING
    status_message: str = "Waiting to start..."
    progress: int = 0
    
    # Input parameters
    gender: str = "any"
    ethnicity: str = "any"
    origin: str = "any"
    role: str = "Software Developer"
    age_range: str = "25-35"
    expertise: str = "mid"
    remote: bool = False
    
    # Generated data
    cv_data: Optional[dict] = None
    image_path: Optional[str] = None
    pdf_path: Optional[str] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    # Error handling
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for API response."""
        return {
            "id": self.id,
            "status": self.status.value,
            "status_message": self.status_message,
            "progress": self.progress,
            "gender": self.gender,
            "ethnicity": self.ethnicity,
            "origin": self.origin,
            "role": self.role,
            "pdf_path": self.pdf_path,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message
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
        import random
        from uuid import uuid4
        
        batch_id = str(uuid4())[:8]
        tasks = []
        
        for i in range(qty):
            task_id = str(uuid4())[:8]
            
            # Randomly select from the provided options
            selected_gender = random.choice(genders) if genders else "any"
            selected_ethnicity = random.choice(ethnicities) if ethnicities else "any"
            selected_origin = random.choice(origins) if origins else "any"
            selected_role = random.choice(roles) if roles else "Software Developer"
            selected_expertise = random.choice(expertise_levels) if expertise_levels else "mid"
            
            # Generate random age within the specified range
            selected_age = random.randint(age_min, age_max)
            age_range = f"{selected_age}"  # Store as single age
            
            task = Task(
                id=task_id,
                batch_id=batch_id,
                gender=selected_gender,
                ethnicity=selected_ethnicity,
                origin=selected_origin,
                role=selected_role,
                age_range=age_range,
                expertise=selected_expertise,
                remote=remote,
                status=TaskStatus.PENDING,
                status_message="Queued for generation",
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
    
    async def update_task_status(
        self,
        task: Task,
        status: TaskStatus,
        message: str = "",
        progress: int = 0
    ):
        """Update a task's status."""
        async with self._lock:
            task.status = status
            task.status_message = message
            task.progress = progress
            
            if status == TaskStatus.COMPLETE:
                task.completed_at = datetime.now()
    
    async def set_task_error(self, task: Task, error_message: str):
        """Mark a task as failed with an error message."""
        async with self._lock:
            task.status = TaskStatus.ERROR
            task.status_message = "Generation failed"
            task.error_message = error_message
            task.completed_at = datetime.now()
    
    def get_all_batches(self) -> list[Batch]:
        """Get all batches."""
        return list(self.batches.values())
    
    def clear_batches(self):
        """Clear all completed batches."""
        self.batches = {
            k: v for k, v in self.batches.items()
            if not v.is_complete
        }


# Global task manager instance
task_manager = TaskManager()
