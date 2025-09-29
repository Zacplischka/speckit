"""
Streamlit UI Interface Contract
Defines the interface between Streamlit components and repository layer.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Protocol
from enum import Enum
from dataclasses import dataclass

from src.models.task import Task


class ViewMode(Enum):
    """UI view modes for task display filtering."""
    ACTIVE_TASKS = "active_tasks"
    COMPLETED_TASKS = "completed_tasks"
    ALL_TASKS = "all_tasks"


@dataclass
class TaskFormData:
    """Form data for new task creation."""
    description: str = ""
    is_valid: bool = False
    error_message: Optional[str] = None

    def validate(self) -> bool:
        """Validate form data and set error message if invalid."""
        description = self.description.strip()

        if not description:
            self.error_message = "Task description cannot be empty"
            self.is_valid = False
            return False

        if len(description) > 500:
            self.error_message = "Task description must be 500 characters or less"
            self.is_valid = False
            return False

        self.error_message = None
        self.is_valid = True
        return True


@dataclass
class UIState:
    """Current UI state for the Streamlit application."""
    current_view: ViewMode = ViewMode.ACTIVE_TASKS
    selected_task_id: Optional[int] = None
    form_data: TaskFormData = None

    def __post_init__(self):
        if self.form_data is None:
            self.form_data = TaskFormData()


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

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
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


# UI Component Interfaces

class TaskDisplayComponent(Protocol):
    """Protocol for task display components."""

    def render_task(self, task: Task, actions_enabled: bool = True) -> None:
        """Render a single task with optional actions."""
        ...


class TaskListComponent(Protocol):
    """Protocol for task list components."""

    def render_task_list(self, tasks: List[Task], view_mode: ViewMode) -> None:
        """Render a list of tasks with appropriate filtering."""
        ...


class TaskFormComponent(Protocol):
    """Protocol for task creation form."""

    def render_task_form(self, form_data: TaskFormData) -> bool:
        """Render task creation form. Returns True if form was submitted."""
        ...