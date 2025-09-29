"""
UI data classes for Streamlit task management application.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


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