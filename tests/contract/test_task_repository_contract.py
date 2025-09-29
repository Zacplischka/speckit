"""
Contract tests for TaskRepository interface.
These tests MUST fail before implementation and pass after.
"""

import pytest
from datetime import datetime
from src.models.task import Task, TaskStatus
from src.database.repository import SQLiteTaskRepository


class TestTaskRepositoryCreateTask:
    """Contract tests for TaskRepository.create_task() method."""

    def test_create_task_returns_task_with_assigned_id(self):
        """Test that create_task() returns Task with assigned ID."""
        repo = SQLiteTaskRepository(":memory:")
        task = repo.create_task("Buy groceries")

        assert task.id is not None
        assert isinstance(task.id, int)
        assert task.id > 0

    def test_create_task_sets_status_to_pending(self):
        """Test that create_task() sets status to 'pending'."""
        repo = SQLiteTaskRepository(":memory:")
        task = repo.create_task("Buy groceries")

        assert task.status == 'pending'

    def test_create_task_sets_created_at_timestamp(self):
        """Test that create_task() sets created_at timestamp."""
        repo = SQLiteTaskRepository(":memory:")
        from datetime import datetime, timezone
        before = datetime.now(timezone.utc).replace(tzinfo=None)  # Convert to UTC naive
        task = repo.create_task("Buy groceries")
        after = datetime.now(timezone.utc).replace(tzinfo=None)   # Convert to UTC naive

        assert task.created_at is not None
        assert isinstance(task.created_at, datetime)
        # Allow for timing differences (SQLite only has second precision)
        assert abs((task.created_at - before).total_seconds()) <= 1
        assert abs((after - task.created_at).total_seconds()) <= 1

    def test_create_task_validates_non_empty_description(self):
        """Test that create_task() validates non-empty description."""
        repo = SQLiteTaskRepository(":memory:")
        task = repo.create_task("Valid description")

        assert task.description == "Valid description"
        assert len(task.description) > 0

    def test_create_task_raises_value_error_for_empty_description(self):
        """Test that create_task() raises ValueError for empty description."""
        repo = SQLiteTaskRepository(":memory:")

        with pytest.raises(ValueError, match="Description cannot be empty"):
            repo.create_task("")

        with pytest.raises(ValueError, match="Description cannot be empty"):
            repo.create_task(None)


class TestTaskRepositoryMarkCompleted:
    """Contract tests for TaskRepository.mark_completed() method."""

    def test_mark_completed_returns_true_when_marking_pending_task_complete(self):
        """Test that mark_completed() returns True when marking pending task complete."""
        repo = SQLiteTaskRepository(":memory:")
        task = repo.create_task("Test task")

        result = repo.mark_completed(task.id)

        assert result is True

    def test_mark_completed_returns_false_when_task_already_completed(self):
        """Test that mark_completed() returns False when task already completed."""
        repo = SQLiteTaskRepository(":memory:")
        task = repo.create_task("Test task")
        repo.mark_completed(task.id)  # First completion

        result = repo.mark_completed(task.id)  # Second completion attempt

        assert result is False

    def test_mark_completed_returns_false_when_task_id_not_found(self):
        """Test that mark_completed() returns False when task ID not found."""
        repo = SQLiteTaskRepository(":memory:")

        result = repo.mark_completed(99999)  # Non-existent ID

        assert result is False

    def test_mark_completed_sets_completed_at_timestamp_when_completing(self):
        """Test that mark_completed() sets completed_at timestamp when completing."""
        repo = SQLiteTaskRepository(":memory:")
        task = repo.create_task("Test task")
        from datetime import datetime, timezone
        before = datetime.now(timezone.utc).replace(tzinfo=None)

        repo.mark_completed(task.id)

        completed_task = repo.get_task_by_id(task.id)
        after = datetime.now(timezone.utc).replace(tzinfo=None)

        assert completed_task.completed_at is not None
        assert isinstance(completed_task.completed_at, datetime)
        # Allow for timing differences (SQLite only has second precision)
        assert abs((completed_task.completed_at - before).total_seconds()) <= 1
        assert abs((after - completed_task.completed_at).total_seconds()) <= 1


class TestTaskRepositoryQueryMethods:
    """Contract tests for TaskRepository query methods."""

    def test_get_all_tasks_returns_all_tasks_ordered_by_created_at_desc(self):
        """Test that get_all_tasks() returns all tasks ordered by created_at DESC."""
        repo = SQLiteTaskRepository(":memory:")
        task1 = repo.create_task("First task")
        task2 = repo.create_task("Second task")
        task3 = repo.create_task("Third task")

        all_tasks = repo.get_all_tasks()

        assert len(all_tasks) == 3
        # Should be ordered by created_at DESC (newest first)
        assert all_tasks[0].id == task3.id
        assert all_tasks[1].id == task2.id
        assert all_tasks[2].id == task1.id

    def test_get_pending_tasks_returns_only_pending_tasks(self):
        """Test that get_pending_tasks() returns only pending tasks."""
        repo = SQLiteTaskRepository(":memory:")
        task1 = repo.create_task("Pending task 1")
        task2 = repo.create_task("To be completed")
        task3 = repo.create_task("Pending task 2")

        repo.mark_completed(task2.id)  # Complete one task

        pending_tasks = repo.get_pending_tasks()

        assert len(pending_tasks) == 2
        pending_ids = [task.id for task in pending_tasks]
        assert task1.id in pending_ids
        assert task3.id in pending_ids
        assert task2.id not in pending_ids

        # All returned tasks should be pending
        for task in pending_tasks:
            assert task.status == 'pending'

    def test_get_completed_tasks_returns_only_completed_tasks_ordered_by_completed_at_desc(self):
        """Test that get_completed_tasks() returns only completed tasks ordered by completed_at DESC."""
        repo = SQLiteTaskRepository(":memory:")
        task1 = repo.create_task("To be completed first")
        task2 = repo.create_task("Pending task")
        task3 = repo.create_task("To be completed second")

        repo.mark_completed(task1.id)  # Complete first

        # Ensure different completion timestamps by adding a small delay
        import time
        time.sleep(1)

        repo.mark_completed(task3.id)  # Complete second

        completed_tasks = repo.get_completed_tasks()

        assert len(completed_tasks) == 2
        # Should be ordered by completed_at DESC (newest completion first)
        assert completed_tasks[0].id == task3.id
        assert completed_tasks[1].id == task1.id

        # All returned tasks should be completed
        for task in completed_tasks:
            assert task.status == 'completed'
            assert task.completed_at is not None

    def test_get_task_by_id_returns_correct_task_or_none(self):
        """Test that get_task_by_id() returns correct task or None."""
        repo = SQLiteTaskRepository(":memory:")
        task = repo.create_task("Test task")

        # Test retrieving existing task
        retrieved_task = repo.get_task_by_id(task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.description == task.description
        assert retrieved_task.status == task.status

        # Test retrieving non-existent task
        non_existent = repo.get_task_by_id(99999)
        assert non_existent is None