"""
Task Repository Contract
Defines the interface for task data operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Literal

TaskStatus = Literal['pending', 'completed']

@dataclass
class Task:
    """Task entity model."""
    id: Optional[int]
    description: str
    status: TaskStatus
    created_at: datetime
    completed_at: Optional[datetime] = None

class TaskRepository(ABC):
    """Abstract interface for task data operations."""

    @abstractmethod
    def create_task(self, description: str) -> Task:
        """
        Create a new task with pending status.

        Args:
            description: Task description text (must not be empty)

        Returns:
            Task: Created task with assigned ID and timestamps

        Raises:
            ValueError: If description is empty or None
        """
        pass

    @abstractmethod
    def mark_completed(self, task_id: int) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: ID of task to mark complete

        Returns:
            bool: True if task was marked complete, False if task not found or already complete
        """
        pass

    @abstractmethod
    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks ordered by creation time (newest first).

        Returns:
            List[Task]: All tasks in the system
        """
        pass

    @abstractmethod
    def get_pending_tasks(self) -> List[Task]:
        """
        Retrieve only pending tasks ordered by creation time (newest first).

        Returns:
            List[Task]: All pending tasks
        """
        pass

    @abstractmethod
    def get_completed_tasks(self) -> List[Task]:
        """
        Retrieve only completed tasks ordered by completion time (newest first).

        Returns:
            List[Task]: All completed tasks
        """
        pass

    @abstractmethod
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a specific task by ID.

        Args:
            task_id: ID of task to retrieve

        Returns:
            Optional[Task]: Task if found, None otherwise
        """
        pass