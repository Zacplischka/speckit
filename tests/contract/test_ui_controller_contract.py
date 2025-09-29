"""
Contract tests for StreamlitUIController interface.
These tests MUST fail before implementation and pass after.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.models.task import Task, TaskStatus
from src.database.repository import SQLiteTaskRepository


# Import the actual implementations
from src.ui.controller import StreamlitUIController
from src.ui.models import ViewMode, TaskFormData, UIState


class TestStreamlitUIController:
    """Contract tests for StreamlitUIController implementation."""

    def setup_method(self):
        """Set up test repository with sample data."""
        self.repo = SQLiteTaskRepository(":memory:")
        self.task1 = self.repo.create_task("Active task 1")
        self.task2 = self.repo.create_task("Active task 2")
        self.task3 = self.repo.create_task("Task to complete")
        self.repo.mark_completed(self.task3.id)

        self.controller = StreamlitUIController(self.repo)

    def test_get_tasks_for_view_active_returns_pending_tasks(self):
        """Test that get_tasks_for_view with ACTIVE_TASKS returns pending tasks."""
        tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)

        assert len(tasks) == 2
        task_ids = [t.id for t in tasks]
        assert self.task1.id in task_ids
        assert self.task2.id in task_ids
        assert self.task3.id not in task_ids  # Completed task shouldn't be included

    def test_get_tasks_for_view_completed_returns_completed_tasks(self):
        """Test that get_tasks_for_view with COMPLETED_TASKS returns completed tasks."""
        tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)

        assert len(tasks) == 1
        assert tasks[0].id == self.task3.id
        assert tasks[0].status == 'completed'

    def test_get_tasks_for_view_all_returns_all_tasks(self):
        """Test that get_tasks_for_view with ALL_TASKS returns all tasks."""
        tasks = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)

        assert len(tasks) == 3
        task_ids = [t.id for t in tasks]
        assert self.task1.id in task_ids
        assert self.task2.id in task_ids
        assert self.task3.id in task_ids

    def test_create_new_task_with_valid_form_data(self):
        """Test that create_new_task works with valid form data."""
        form_data = TaskFormData("New valid task")
        form_data.is_valid = True

        result = self.controller.create_new_task(form_data)

        assert result is True

        # Verify task was actually created
        all_tasks = self.repo.get_all_tasks()
        assert len(all_tasks) == 4  # 3 existing + 1 new
        new_task = [t for t in all_tasks if t.description == "New valid task"][0]
        assert new_task.status == 'pending'

    def test_create_new_task_with_invalid_form_data(self):
        """Test that create_new_task fails with invalid form data."""
        form_data = TaskFormData("")  # Empty description

        result = self.controller.create_new_task(form_data)

        assert result is False
        assert form_data.error_message is not None

    def test_complete_task_marks_task_as_completed(self):
        """Test that complete_task marks task as completed."""
        result = self.controller.complete_task(self.task1.id)

        assert result is True

        # Verify task is now completed
        updated_task = self.repo.get_task_by_id(self.task1.id)
        assert updated_task.status == 'completed'
        assert updated_task.completed_at is not None

    def test_complete_task_returns_false_for_nonexistent_task(self):
        """Test that complete_task returns False for non-existent task."""
        result = self.controller.complete_task(999)

        assert result is False

    def test_delete_task_removes_task(self):
        """Test that delete_task removes task from repository."""
        result = self.controller.delete_task(self.task1.id)

        assert result is True

        # Verify task is removed
        deleted_task = self.repo.get_task_by_id(self.task1.id)
        assert deleted_task is None

    def test_delete_task_returns_false_for_nonexistent_task(self):
        """Test that delete_task returns False for non-existent task."""
        result = self.controller.delete_task(999)

        assert result is False

    def test_validate_task_form_with_valid_data(self):
        """Test that validate_task_form returns True for valid data."""
        form_data = TaskFormData("Valid task description")

        result = self.controller.validate_task_form(form_data)

        assert result is True
        assert form_data.is_valid is True
        assert form_data.error_message is None

    def test_validate_task_form_with_invalid_data(self):
        """Test that validate_task_form returns False for invalid data."""
        form_data = TaskFormData("")  # Empty description

        result = self.controller.validate_task_form(form_data)

        assert result is False
        assert form_data.is_valid is False
        assert form_data.error_message is not None


class TestTaskFormDataValidation:
    """Contract tests for TaskFormData validation."""

    def test_validate_with_valid_description(self):
        """Test that validate returns True for valid description."""
        form_data = TaskFormData("Valid task description")

        result = form_data.validate()

        assert result is True
        assert form_data.is_valid is True
        assert form_data.error_message is None

    def test_validate_with_empty_description(self):
        """Test that validate returns False for empty description."""
        form_data = TaskFormData("")

        result = form_data.validate()

        assert result is False
        assert form_data.is_valid is False
        assert "cannot be empty" in form_data.error_message

    def test_validate_with_whitespace_only_description(self):
        """Test that validate returns False for whitespace-only description."""
        form_data = TaskFormData("   \t\n   ")

        result = form_data.validate()

        assert result is False
        assert form_data.is_valid is False
        assert "cannot be empty" in form_data.error_message

    def test_validate_with_too_long_description(self):
        """Test that validate returns False for description over 500 chars."""
        form_data = TaskFormData("a" * 501)  # 501 characters

        result = form_data.validate()

        assert result is False
        assert form_data.is_valid is False
        assert "500 characters" in form_data.error_message


class TestUIState:
    """Contract tests for UIState data class."""

    def test_ui_state_initializes_with_defaults(self):
        """Test that UIState initializes with proper defaults."""
        state = UIState()

        assert state.current_view == ViewMode.ACTIVE_TASKS
        assert state.selected_task_id is None
        assert state.form_data is not None
        assert isinstance(state.form_data, TaskFormData)

    def test_ui_state_with_custom_form_data(self):
        """Test that UIState accepts custom form data."""
        custom_form = TaskFormData("Custom task")
        state = UIState()
        state.form_data = custom_form

        assert state.form_data.description == "Custom task"