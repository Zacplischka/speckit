"""
Integration test for task creation workflow.
This test MUST fail before implementation and pass after.
"""

import pytest
from unittest.mock import Mock, patch
from src.models.task import Task, TaskStatus
from src.database.repository import SQLiteTaskRepository


# Import UI components
from src.ui.controller import StreamlitUIController
from src.ui.models import ViewMode, TaskFormData


class TestTaskCreationIntegration:
    """Integration tests for the complete task creation workflow."""

    def setup_method(self):
        """Set up test environment with repository and controller."""
        self.repo = SQLiteTaskRepository(":memory:")
        self.controller = StreamlitUIController(self.repo)

    def test_complete_task_creation_workflow(self):
        """Test the complete workflow from form input to database storage."""
        # Step 1: User enters task description
        user_input = "Buy groceries for the week"
        form_data = TaskFormData(user_input)

        # Step 2: Form validation passes
        is_valid = self.controller.validate_task_form(form_data)
        assert is_valid is True

        # Step 3: Task creation through controller
        creation_result = self.controller.create_new_task(form_data)
        assert creation_result is True

        # Step 4: Verify task appears in active tasks view
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 1

        created_task = active_tasks[0]
        assert created_task.description == user_input
        assert created_task.status == 'pending'
        assert created_task.id is not None
        assert created_task.created_at is not None
        assert created_task.completed_at is None

    def test_task_creation_with_whitespace_trimming(self):
        """Test that task creation trims whitespace from input."""
        # User input with extra whitespace
        user_input = "  Clean the house  \t\n  "
        expected_description = "Clean the house"

        form_data = TaskFormData(user_input)

        # Form validation should pass after trimming
        is_valid = self.controller.validate_task_form(form_data)
        assert is_valid is True

        # Task creation
        creation_result = self.controller.create_new_task(form_data)
        assert creation_result is True

        # Verify task has trimmed description
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 1
        assert active_tasks[0].description == expected_description

    def test_task_creation_failure_with_empty_input(self):
        """Test that task creation fails gracefully with empty input."""
        # Empty input
        form_data = TaskFormData("")

        # Form validation should fail
        is_valid = self.controller.validate_task_form(form_data)
        assert is_valid is False
        assert form_data.error_message is not None

        # Task creation should fail
        creation_result = self.controller.create_new_task(form_data)
        assert creation_result is False

        # No tasks should be created
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 0

    def test_task_creation_failure_with_too_long_input(self):
        """Test that task creation fails with overly long input."""
        # Input that's too long (over 500 characters)
        long_input = "a" * 501
        form_data = TaskFormData(long_input)

        # Form validation should fail
        is_valid = self.controller.validate_task_form(form_data)
        assert is_valid is False
        assert "500 characters" in form_data.error_message

        # Task creation should fail
        creation_result = self.controller.create_new_task(form_data)
        assert creation_result is False

        # No tasks should be created
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 0

    def test_multiple_task_creation_workflow(self):
        """Test creating multiple tasks in sequence."""
        task_descriptions = [
            "First task",
            "Second task",
            "Third task"
        ]

        # Create tasks one by one
        for i, description in enumerate(task_descriptions):
            form_data = TaskFormData(description)

            # Validate and create each task
            is_valid = self.controller.validate_task_form(form_data)
            assert is_valid is True

            creation_result = self.controller.create_new_task(form_data)
            assert creation_result is True

            # Verify task count increases
            active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
            assert len(active_tasks) == i + 1

        # Verify all tasks are present with correct descriptions
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        task_descriptions_from_db = [task.description for task in active_tasks]

        for expected_desc in task_descriptions:
            assert expected_desc in task_descriptions_from_db

    @patch('src.database.repository.SQLiteTaskRepository.create_task')
    def test_task_creation_handles_database_errors(self, mock_create_task):
        """Test that task creation handles database errors gracefully."""
        # Mock database error
        mock_create_task.side_effect = RuntimeError("Database connection failed")

        form_data = TaskFormData("Valid task description")

        # Form validation should pass
        is_valid = self.controller.validate_task_form(form_data)
        assert is_valid is True

        # Task creation should fail due to database error
        creation_result = self.controller.create_new_task(form_data)
        assert creation_result is False

        # Error message should be set
        assert form_data.error_message is not None
        assert "Failed to create task" in form_data.error_message