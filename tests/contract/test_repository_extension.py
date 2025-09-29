"""
Contract tests for TaskRepository delete_task extension.
These tests MUST fail before implementation and pass after.
"""

import pytest
from src.models.task import Task, TaskStatus
from src.database.repository import SQLiteTaskRepository


class TestTaskRepositoryDeleteTask:
    """Contract tests for TaskRepository.delete_task() method."""

    def test_delete_task_returns_true_when_task_exists(self):
        """Test that delete_task() returns True when task exists."""
        repo = SQLiteTaskRepository(":memory:")
        task = repo.create_task("Task to delete")

        result = repo.delete_task(task.id)

        assert result is True

    def test_delete_task_returns_false_when_task_not_found(self):
        """Test that delete_task() returns False when task doesn't exist."""
        repo = SQLiteTaskRepository(":memory:")

        result = repo.delete_task(999)  # Non-existent ID

        assert result is False

    def test_delete_task_removes_task_from_database(self):
        """Test that delete_task() actually removes task from database."""
        repo = SQLiteTaskRepository(":memory:")
        task = repo.create_task("Task to delete")

        # Verify task exists before deletion
        found_task = repo.get_task_by_id(task.id)
        assert found_task is not None

        # Delete the task
        result = repo.delete_task(task.id)
        assert result is True

        # Verify task no longer exists
        deleted_task = repo.get_task_by_id(task.id)
        assert deleted_task is None

    def test_delete_task_removes_from_all_task_lists(self):
        """Test that deleted task doesn't appear in any task lists."""
        repo = SQLiteTaskRepository(":memory:")
        task1 = repo.create_task("Keep this task")
        task2 = repo.create_task("Delete this task")
        repo.mark_completed(task2.id)  # Make it completed first

        # Verify both tasks exist in appropriate lists
        all_tasks = repo.get_all_tasks()
        assert len(all_tasks) == 2

        completed_tasks = repo.get_completed_tasks()
        assert len(completed_tasks) == 1
        assert completed_tasks[0].id == task2.id

        # Delete the completed task
        result = repo.delete_task(task2.id)
        assert result is True

        # Verify task is removed from all lists
        all_tasks_after = repo.get_all_tasks()
        assert len(all_tasks_after) == 1
        assert all_tasks_after[0].id == task1.id

        completed_tasks_after = repo.get_completed_tasks()
        assert len(completed_tasks_after) == 0

    def test_delete_task_handles_database_errors(self):
        """Test that delete_task() handles database errors appropriately."""
        repo = SQLiteTaskRepository(":memory:")

        # This test would need to simulate a database error
        # For now, just verify the method signature exists
        try:
            result = repo.delete_task(1)
            # Should return False for non-existent task, not raise exception
            assert isinstance(result, bool)
        except RuntimeError:
            # RuntimeError is acceptable for database failures
            pass
        except AttributeError:
            # This will fail until delete_task is implemented
            pytest.fail("delete_task method not implemented")