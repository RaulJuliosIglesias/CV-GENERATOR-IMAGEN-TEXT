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
    cv_data: Optional[dict] = None
    image_path: Optional[str] = None
    pdf_path: Optional[str] = None
    html_path: Optional[str] = None
    error: Optional[str] = None
    progress: int = 0
    message: str = "Initialized"
    
    # Subtasks tracking
    subtasks: list[Subtask] = field(default_factory=lambda: [
        Subtask(id="1", name="Generate Text (LLM)"),
        Subtask(id="2", name="Generate Image (AI)"),
        Subtask(id="3", name="Assemble HTML"),
        Subtask(id="4", name="Create PDF")
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
            
            # Randomly select from the provided options
            selected_gender = random.choice(genders) if genders else "any"
            selected_ethnicity = random.choice(ethnicities) if ethnicities else "any"
            selected_origin = random.choice(origins) if origins else "any"
            selected_role = random.choice(roles) if roles else "Software Developer"
            selected_expertise = random.choice(expertise_levels) if expertise_levels else "mid"
            
            # Generate random age within the specified range
            selected_age = random.randint(age_min, age_max)
            age_range = f"{selected_age}"
            
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
    
    def clear_batches(self):
        """Clear all completed batches."""
        self.batches = {
            k: v for k, v in self.batches.items()
            if not v.is_complete
        }


# Global task manager instance
task_manager = TaskManager()
