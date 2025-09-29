"""
Integration test for task deletion workflow.
This test MUST fail before implementation and pass after.
"""

import pytest
from src.models.task import Task, TaskStatus
from src.database.repository import SQLiteTaskRepository


# Import UI components
from src.ui.controller import StreamlitUIController
from src.ui.models import ViewMode


class TestTaskDeletionIntegration:
    """Integration tests for the complete task deletion workflow."""

    def setup_method(self):
        """Set up test environment with repository, controller, and sample tasks."""
        self.repo = SQLiteTaskRepository(":memory:")
        self.controller = StreamlitUIController(self.repo)

        # Create test tasks in different states
        self.active_task1 = self.repo.create_task("Delete this active task")
        self.active_task2 = self.repo.create_task("Keep this active task")
        self.completed_task1 = self.repo.create_task("Delete this completed task")
        self.completed_task2 = self.repo.create_task("Keep this completed task")

        # Mark some tasks as completed
        self.repo.mark_completed(self.completed_task1.id)
        self.repo.mark_completed(self.completed_task2.id)

    def test_delete_active_task_workflow(self):
        """Test the complete workflow of deleting an active task."""
        # Step 1: Verify task exists in active view
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 2
        task_ids = [t.id for t in active_tasks]
        assert self.active_task1.id in task_ids

        # Step 2: User clicks "Delete" button - controller deletes task
        deletion_result = self.controller.delete_task(self.active_task1.id)
        assert deletion_result is True

        # Step 3: Verify task is removed from active view
        active_tasks_after = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks_after) == 1
        assert self.active_task1.id not in [t.id for t in active_tasks_after]
        assert self.active_task2.id in [t.id for t in active_tasks_after]

        # Step 4: Verify task is completely removed from database
        deleted_task = self.repo.get_task_by_id(self.active_task1.id)
        assert deleted_task is None

    def test_delete_completed_task_workflow(self):
        """Test the complete workflow of deleting a completed task."""
        # Step 1: Verify task exists in completed view
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks) == 2
        task_ids = [t.id for t in completed_tasks]
        assert self.completed_task1.id in task_ids

        # Step 2: User clicks "Delete" button - controller deletes task
        deletion_result = self.controller.delete_task(self.completed_task1.id)
        assert deletion_result is True

        # Step 3: Verify task is removed from completed view
        completed_tasks_after = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks_after) == 1
        assert self.completed_task1.id not in [t.id for t in completed_tasks_after]
        assert self.completed_task2.id in [t.id for t in completed_tasks_after]

        # Step 4: Verify task is completely removed from database
        deleted_task = self.repo.get_task_by_id(self.completed_task1.id)
        assert deleted_task is None

    def test_delete_task_removes_from_all_views(self):
        """Test that deleted task is removed from all views."""
        # Initial state verification
        all_tasks_before = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        assert len(all_tasks_before) == 4

        # Delete a task
        deletion_result = self.controller.delete_task(self.active_task1.id)
        assert deletion_result is True

        # Verify task is removed from all views
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        all_tasks = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)

        assert len(active_tasks) == 1  # Only active_task2
        assert len(completed_tasks) == 2  # Both completed tasks
        assert len(all_tasks) == 3  # Total: 1 active + 2 completed

        # Verify deleted task is not in any view
        all_task_ids = [t.id for t in all_tasks]
        assert self.active_task1.id not in all_task_ids

    def test_delete_nonexistent_task_fails(self):
        """Test that attempting to delete non-existent task fails gracefully."""
        # Get initial task counts
        initial_active_count = len(self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS))
        initial_completed_count = len(self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS))

        # Try to delete a task that doesn't exist
        deletion_result = self.controller.delete_task(999)
        assert deletion_result is False

        # Verify no changes to task lists
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)

        assert len(active_tasks) == initial_active_count
        assert len(completed_tasks) == initial_completed_count

    def test_delete_multiple_tasks_workflow(self):
        """Test deleting multiple tasks in sequence."""
        # Delete both active tasks
        deletion_result1 = self.controller.delete_task(self.active_task1.id)
        assert deletion_result1 is True

        deletion_result2 = self.controller.delete_task(self.active_task2.id)
        assert deletion_result2 is True

        # Verify no active tasks remain
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 0

        # Verify completed tasks are unaffected
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks) == 2

        # Verify total count
        all_tasks = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        assert len(all_tasks) == 2  # Only completed tasks remain

    def test_delete_all_tasks_workflow(self):
        """Test deleting all tasks leaves empty lists."""
        # Delete all tasks
        task_ids = [
            self.active_task1.id,
            self.active_task2.id,
            self.completed_task1.id,
            self.completed_task2.id
        ]

        for task_id in task_ids:
            deletion_result = self.controller.delete_task(task_id)
            assert deletion_result is True

        # Verify all views are empty
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        all_tasks = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)

        assert len(active_tasks) == 0
        assert len(completed_tasks) == 0
        assert len(all_tasks) == 0

    def test_delete_task_permanent_removal(self):
        """Test that deletion is permanent and task cannot be recovered."""
        # Get task data before deletion
        task_to_delete = self.repo.get_task_by_id(self.active_task1.id)
        assert task_to_delete is not None
        original_description = task_to_delete.description

        # Delete the task
        deletion_result = self.controller.delete_task(self.active_task1.id)
        assert deletion_result is True

        # Verify task cannot be found by ID
        deleted_task = self.repo.get_task_by_id(self.active_task1.id)
        assert deleted_task is None

        # Verify task is not in any repository method results
        all_tasks = self.repo.get_all_tasks()
        pending_tasks = self.repo.get_pending_tasks()
        completed_tasks = self.repo.get_completed_tasks()

        all_descriptions = [t.description for t in all_tasks]
        pending_descriptions = [t.description for t in pending_tasks]
        completed_descriptions = [t.description for t in completed_tasks]

        assert original_description not in all_descriptions
        assert original_description not in pending_descriptions
        assert original_description not in completed_descriptions

    def test_delete_task_error_handling(self):
        """Test that task deletion handles repository errors gracefully."""
        from unittest.mock import patch

        with patch.object(self.repo, 'delete_task') as mock_delete_task:
            # Mock a database error
            mock_delete_task.side_effect = RuntimeError("Database connection failed")

            # Attempt to delete task
            deletion_result = self.controller.delete_task(self.active_task1.id)

            # Should return False on error
            assert deletion_result is False

            # Verify task still exists (deletion didn't happen)
            task = self.repo.get_task_by_id(self.active_task1.id)
            assert task is not None
            assert task.status == 'pending'

    def test_delete_task_idempotence(self):
        """Test that deleting the same task twice doesn't cause errors."""
        # Delete task first time
        deletion_result1 = self.controller.delete_task(self.active_task1.id)
        assert deletion_result1 is True

        # Verify task is gone
        deleted_task = self.repo.get_task_by_id(self.active_task1.id)
        assert deleted_task is None

        # Try to delete the same task again
        deletion_result2 = self.controller.delete_task(self.active_task1.id)
        assert deletion_result2 is False  # Should return False for non-existent task

        # Verify no side effects
        all_tasks = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        assert len(all_tasks) == 3  # Same as after first deletion