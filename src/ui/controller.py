"""
UI controller for Streamlit task management application.
Handles business logic between UI components and repository.
"""

from abc import ABC, abstractmethod
from typing import List, Protocol
from src.models.task import Task
from src.ui.models import ViewMode, TaskFormData


class TaskRepository(Protocol):
    """
    Protocol defining the repository interface required by the UI.
    This matches the existing SQLiteTaskRepository interface.
    """

    def create_task(self, description: str) -> Task:
        """Create a new task with pending status."""
        ...

    def mark_completed(self, task_id: int) -> bool:
        """Mark a task as completed."""
        ...

    def delete_task(self, task_id: int) -> bool:
        """Delete a task permanently."""
        ...

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks."""
        ...

    def get_pending_tasks(self) -> List[Task]:
        """Retrieve only pending tasks."""
        ...

    def get_completed_tasks(self) -> List[Task]:
        """Retrieve only completed tasks."""
        ...

    def get_task_by_id(self, task_id: int) -> Task:
        """Retrieve a specific task by ID."""
        ...


class UIController(ABC):
    """
    Abstract controller for UI operations.
    Handles business logic between UI components and repository.
    """

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    @abstractmethod
    def get_tasks_for_view(self, view_mode: ViewMode) -> List[Task]:
        """Get tasks filtered by current view mode."""
        pass

    @abstractmethod
    def create_new_task(self, form_data: TaskFormData) -> bool:
        """Create a new task from form data."""
        pass

    @abstractmethod
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed."""
        pass

    @abstractmethod
    def delete_task(self, task_id: int) -> bool:
        """Delete a task permanently."""
        pass

    @abstractmethod
    def validate_task_form(self, form_data: TaskFormData) -> bool:
        """Validate task form data."""
        pass


class StreamlitUIController(UIController):
    """
    Concrete implementation of UI controller for Streamlit.
    """

    def get_tasks_for_view(self, view_mode: ViewMode) -> List[Task]:
        """Get tasks filtered by current view mode."""
        if view_mode == ViewMode.ACTIVE_TASKS:
            return self.repository.get_pending_tasks()
        elif view_mode == ViewMode.COMPLETED_TASKS:
            return self.repository.get_completed_tasks()
        else:  # ALL_TASKS
            return self.repository.get_all_tasks()

    def create_new_task(self, form_data: TaskFormData) -> bool:
        """Create a new task from form data."""
        if not self.validate_task_form(form_data):
            return False

        try:
            self.repository.create_task(form_data.description.strip())
            return True
        except (ValueError, RuntimeError):
            form_data.error_message = "Failed to create task. Please try again."
            return False

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed."""
        try:
            return self.repository.mark_completed(task_id)
        except RuntimeError:
            return False

    def delete_task(self, task_id: int) -> bool:
        """Delete a task permanently."""
        try:
            return self.repository.delete_task(task_id)
        except RuntimeError:
            return False

    def validate_task_form(self, form_data: TaskFormData) -> bool:
        """Validate task form data."""
        return form_data.validate()