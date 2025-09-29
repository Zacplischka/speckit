"""
Quickstart scenario validation tests.
Ensures that all scenarios described in quickstart.md work correctly.
"""

import pytest
from src.database.repository import SQLiteTaskRepository
from src.ui.controller import StreamlitUIController
from src.ui.models import ViewMode, TaskFormData


class TestQuickstartScenarios:
    """Test the scenarios described in quickstart.md."""

    def setup_method(self):
        """Set up test environment."""
        self.repo = SQLiteTaskRepository(":memory:")
        self.controller = StreamlitUIController(self.repo)

    def test_quickstart_step_4_basic_functionality(self):
        """Test the 4-step workflow from quickstart.md Step 4."""

        # Step 1: Add a Task - Enter "Buy groceries" and click "Add Task"
        form_data = TaskFormData("Buy groceries")
        assert self.controller.validate_task_form(form_data) is True
        assert self.controller.create_new_task(form_data) is True

        # Verify task was created and appears in active tasks
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 1
        task = active_tasks[0]
        assert task.description == "Buy groceries"
        assert task.status == 'pending'

        # Step 2: Mark Complete - Click "✓ Complete" button next to your task
        assert self.controller.complete_task(task.id) is True

        # Verify task moved to completed
        active_tasks_after = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks_after) == 0

        # Step 3: View Completed - Use sidebar to switch to "Completed Tasks"
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks) == 1
        completed_task = completed_tasks[0]
        assert completed_task.description == "Buy groceries"
        assert completed_task.status == 'completed'
        assert completed_task.completed_at is not None

        # Step 4: Delete Task - Click "🗑 Delete" button to remove task permanently
        assert self.controller.delete_task(completed_task.id) is True

        # Verify task is completely removed
        all_tasks_final = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        assert len(all_tasks_final) == 0

    def test_form_validation_scenarios(self):
        """Test form validation scenarios from quickstart.md."""

        # Test empty task description fails
        empty_form = TaskFormData("")
        assert self.controller.validate_task_form(empty_form) is False
        assert "cannot be empty" in empty_form.error_message
        assert self.controller.create_new_task(empty_form) is False

        # Test whitespace only fails
        whitespace_form = TaskFormData("   ")
        assert self.controller.validate_task_form(whitespace_form) is False
        assert "cannot be empty" in whitespace_form.error_message

        # Test maximum length validation
        long_form = TaskFormData("a" * 501)
        assert self.controller.validate_task_form(long_form) is False
        assert "500 characters" in long_form.error_message

        # Test valid task description passes
        valid_form = TaskFormData("Valid task description")
        assert self.controller.validate_task_form(valid_form) is True
        assert valid_form.error_message is None

    def test_database_integration_scenarios(self):
        """Test database integration scenarios from quickstart.md."""

        # Create mixed task states as described in quickstart
        task1 = self.controller.create_new_task(TaskFormData("Active task"))
        task2_form = TaskFormData("To complete")
        self.controller.create_new_task(task2_form)

        # Get the second task and complete it
        all_tasks = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        task2 = next(t for t in all_tasks if t.description == "To complete")
        self.controller.complete_task(task2.id)

        # Test view filtering as described
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 1
        assert active_tasks[0].status == "pending"

        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks) == 1
        assert completed_tasks[0].status == "completed"

    def test_error_handling_scenarios(self):
        """Test error handling scenarios from quickstart.md."""

        # Test operations on non-existent tasks
        assert self.controller.complete_task(999) is False
        assert self.controller.delete_task(999) is False

        # Test task form validation with error messages
        form_data = TaskFormData("")
        assert self.controller.create_new_task(form_data) is False
        assert form_data.error_message is not None

    def test_performance_expectations(self):
        """Test performance expectations from quickstart.md."""
        import time

        # Test that CRUD operations complete quickly (<100ms as specified)

        # Add Task performance
        start_time = time.time()
        form_data = TaskFormData("Performance test task")
        self.controller.create_new_task(form_data)
        add_time = time.time() - start_time
        assert add_time < 0.1  # Less than 100ms

        # Get task ID
        tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        task_id = tasks[0].id

        # Complete Task performance
        start_time = time.time()
        self.controller.complete_task(task_id)
        complete_time = time.time() - start_time
        assert complete_time < 0.1  # Less than 100ms

        # Delete Task performance
        start_time = time.time()
        self.controller.delete_task(task_id)
        delete_time = time.time() - start_time
        assert delete_time < 0.1  # Less than 100ms

        # View Switch performance
        start_time = time.time()
        self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        view_time = time.time() - start_time
        assert view_time < 0.05  # Less than 50ms as specified