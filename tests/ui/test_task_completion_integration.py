"""
Integration test for task completion workflow.
This test MUST fail before implementation and pass after.
"""

import pytest
from datetime import datetime
from src.models.task import Task, TaskStatus
from src.database.repository import SQLiteTaskRepository


# Import UI components
from src.ui.controller import StreamlitUIController
from src.ui.models import ViewMode, TaskFormData


class TestTaskCompletionIntegration:
    """Integration tests for the complete task completion workflow."""

    def setup_method(self):
        """Set up test environment with repository, controller, and sample tasks."""
        self.repo = SQLiteTaskRepository(":memory:")
        self.controller = StreamlitUIController(self.repo)

        # Create some test tasks
        self.active_task1 = self.repo.create_task("Complete this task")
        self.active_task2 = self.repo.create_task("Another active task")
        self.already_completed = self.repo.create_task("Already done")
        self.repo.mark_completed(self.already_completed.id)

    def test_complete_task_workflow_from_active_view(self):
        """Test the complete workflow of marking a task as completed from active view."""
        # Step 1: Verify task is in active tasks
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 2
        target_task = None
        for task in active_tasks:
            if task.id == self.active_task1.id:
                target_task = task
                break
        assert target_task is not None
        assert target_task.status == 'pending'

        # Step 2: User clicks "Complete" button - controller marks task complete
        completion_result = self.controller.complete_task(self.active_task1.id)
        assert completion_result is True

        # Step 3: Verify task is removed from active view
        active_tasks_after = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks_after) == 1
        assert self.active_task1.id not in [t.id for t in active_tasks_after]

        # Step 4: Verify task appears in completed view
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks) == 2  # Our completed task + already_completed

        completed_task = None
        for task in completed_tasks:
            if task.id == self.active_task1.id:
                completed_task = task
                break
        assert completed_task is not None
        assert completed_task.status == 'completed'
        assert completed_task.completed_at is not None

    def test_task_completion_appears_in_all_tasks_view(self):
        """Test that completed task appears correctly in all tasks view."""
        # Mark task as completed
        completion_result = self.controller.complete_task(self.active_task1.id)
        assert completion_result is True

        # Check all tasks view
        all_tasks = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        assert len(all_tasks) == 3  # 2 active + 1 completed (before) = 3 total

        # Find our completed task
        completed_task = None
        for task in all_tasks:
            if task.id == self.active_task1.id:
                completed_task = task
                break

        assert completed_task is not None
        assert completed_task.status == 'completed'
        assert completed_task.completed_at is not None

        # Verify other tasks are still in correct states
        active_count = sum(1 for task in all_tasks if task.status == 'pending')
        completed_count = sum(1 for task in all_tasks if task.status == 'completed')
        assert active_count == 1  # only active_task2
        assert completed_count == 2  # active_task1 + already_completed

    def test_complete_nonexistent_task_fails(self):
        """Test that attempting to complete non-existent task fails gracefully."""
        # Try to complete a task that doesn't exist
        completion_result = self.controller.complete_task(999)
        assert completion_result is False

        # Verify no changes to task lists
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 2

        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks) == 1  # Only already_completed

    def test_complete_already_completed_task(self):
        """Test behavior when attempting to complete an already completed task."""
        # Get the already completed task from database (it was completed in setup)
        already_completed_task = self.repo.get_task_by_id(self.already_completed.id)
        original_completed_at = already_completed_task.completed_at

        # Try to complete an already completed task
        completion_result = self.controller.complete_task(self.already_completed.id)

        # Should return False since task is already completed
        assert completion_result is False

        # Verify completed_at timestamp wasn't changed
        updated_task = self.repo.get_task_by_id(self.already_completed.id)
        assert updated_task.completed_at == original_completed_at

    def test_multiple_task_completion_workflow(self):
        """Test completing multiple tasks in sequence."""
        # Complete both active tasks
        task_ids_to_complete = [self.active_task1.id, self.active_task2.id]

        for task_id in task_ids_to_complete:
            completion_result = self.controller.complete_task(task_id)
            assert completion_result is True

        # Verify no active tasks remain
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 0

        # Verify all tasks are now completed
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks) == 3  # 2 newly completed + already_completed

        # Verify all completed tasks have proper timestamps
        for task in completed_tasks:
            assert task.status == 'completed'
            assert task.completed_at is not None

    def test_task_completion_preserves_other_task_data(self):
        """Test that completing a task preserves all other task data."""
        # Get original task data
        original_task = self.repo.get_task_by_id(self.active_task1.id)
        original_description = original_task.description
        original_created_at = original_task.created_at
        original_id = original_task.id

        # Complete the task
        completion_result = self.controller.complete_task(self.active_task1.id)
        assert completion_result is True

        # Get updated task
        completed_task = self.repo.get_task_by_id(self.active_task1.id)

        # Verify all other data is preserved
        assert completed_task.id == original_id
        assert completed_task.description == original_description
        assert completed_task.created_at == original_created_at

        # Verify only status and completed_at changed
        assert completed_task.status == 'completed'
        assert completed_task.completed_at is not None
        assert completed_task.completed_at != original_task.completed_at  # Should be different (was None)

    def test_task_completion_error_handling(self):
        """Test that task completion handles repository errors gracefully."""
        from unittest.mock import patch

        with patch.object(self.repo, 'mark_completed') as mock_mark_completed:
            # Mock a database error
            mock_mark_completed.side_effect = RuntimeError("Database connection failed")

            # Attempt to complete task
            completion_result = self.controller.complete_task(self.active_task1.id)

            # Should return False on error
            assert completion_result is False

            # Verify task state didn't change
            task = self.repo.get_task_by_id(self.active_task1.id)
            assert task.status == 'pending'
            assert task.completed_at is None