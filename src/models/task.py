"""
Task entity model and related types.
Implementation per contracts/task_repository.py specification.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal

# Type definition for task status
TaskStatus = Literal['pending', 'completed']


@dataclass
class Task:
    """
    Task entity model representing a user-defined action item.

    Attributes:
        id: Unique identifier (None for new tasks, assigned by repository)
        description: Task description text (must not be empty)
        status: Current task status ('pending' or 'completed')
        created_at: Task creation timestamp
        completed_at: Task completion timestamp (None for pending tasks)
    """
    id: Optional[int]
    description: str
    status: TaskStatus
    created_at: datetime
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate task data after initialization."""
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")

        # Ensure description is stripped of whitespace
        self.description = self.description.strip()

        # Validate status transitions and completion timestamp consistency
        if self.status == 'pending' and self.completed_at is not None:
            raise ValueError("Pending tasks cannot have a completion timestamp")

        if self.status == 'completed' and self.completed_at is None:
            raise ValueError("Completed tasks must have a completion timestamp")