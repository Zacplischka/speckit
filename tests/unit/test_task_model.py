"""
Unit tests for Task model validation.
Tests the dataclass and validation logic in isolation.
"""

import pytest
from datetime import datetime
from src.models.task import Task, TaskStatus


class TestTaskModel:
    """Unit tests for Task dataclass and validation."""

    def test_task_creation_with_valid_data(self):
        """Test creating Task with valid data."""
        created_at = datetime.now()
        task = Task(
            id=1,
            description="Test task",
            status='pending',
            created_at=created_at,
            completed_at=None
        )

        assert task.id == 1
        assert task.description == "Test task"
        assert task.status == 'pending'
        assert task.created_at == created_at
        assert task.completed_at is None

    def test_task_creation_with_completion_data(self):
        """Test creating completed Task with valid data."""
        created_at = datetime.now()
        completed_at = datetime.now()
        task = Task(
            id=1,
            description="Completed task",
            status='completed',
            created_at=created_at,
            completed_at=completed_at
        )

        assert task.id == 1
        assert task.description == "Completed task"
        assert task.status == 'completed'
        assert task.created_at == created_at
        assert task.completed_at == completed_at

    def test_task_validation_rejects_empty_description(self):
        """Test that Task validation rejects empty descriptions."""
        with pytest.raises(ValueError, match="Description cannot be empty"):
            Task(
                id=1,
                description="",
                status='pending',
                created_at=datetime.now()
            )

    def test_task_validation_rejects_none_description(self):
        """Test that Task validation rejects None descriptions."""
        with pytest.raises(ValueError, match="Description cannot be empty"):
            Task(
                id=1,
                description=None,
                status='pending',
                created_at=datetime.now()
            )

    def test_task_validation_rejects_whitespace_only_description(self):
        """Test that Task validation rejects whitespace-only descriptions."""
        with pytest.raises(ValueError, match="Description cannot be empty"):
            Task(
                id=1,
                description="   ",
                status='pending',
                created_at=datetime.now()
            )

    def test_task_validation_strips_whitespace_from_description(self):
        """Test that Task validation strips whitespace from descriptions."""
        task = Task(
            id=1,
            description="  Test task  ",
            status='pending',
            created_at=datetime.now()
        )

        assert task.description == "Test task"

    def test_task_validation_rejects_pending_with_completion_timestamp(self):
        """Test that pending tasks cannot have completion timestamps."""
        with pytest.raises(ValueError, match="Pending tasks cannot have a completion timestamp"):
            Task(
                id=1,
                description="Invalid task",
                status='pending',
                created_at=datetime.now(),
                completed_at=datetime.now()
            )

    def test_task_validation_rejects_completed_without_completion_timestamp(self):
        """Test that completed tasks must have completion timestamps."""
        with pytest.raises(ValueError, match="Completed tasks must have a completion timestamp"):
            Task(
                id=1,
                description="Invalid task",
                status='completed',
                created_at=datetime.now(),
                completed_at=None
            )

    def test_task_status_literal_type(self):
        """Test that TaskStatus is properly defined as Literal type."""
        # This test ensures the type hints are correct
        task_pending = Task(
            id=1,
            description="Pending task",
            status='pending',
            created_at=datetime.now()
        )

        task_completed = Task(
            id=2,
            description="Completed task",
            status='completed',
            created_at=datetime.now(),
            completed_at=datetime.now()
        )

        assert task_pending.status == 'pending'
        assert task_completed.status == 'completed'

    def test_task_equality(self):
        """Test Task equality comparison."""
        created_at = datetime.now()
        task1 = Task(
            id=1,
            description="Test task",
            status='pending',
            created_at=created_at
        )

        task2 = Task(
            id=1,
            description="Test task",
            status='pending',
            created_at=created_at
        )

        task3 = Task(
            id=2,
            description="Different task",
            status='pending',
            created_at=created_at
        )

        assert task1 == task2  # Same data
        assert task1 != task3  # Different ID and description

    def test_task_repr(self):
        """Test Task string representation."""
        task = Task(
            id=1,
            description="Test task",
            status='pending',
            created_at=datetime(2025, 9, 29, 12, 0, 0)
        )

        task_repr = repr(task)
        assert "Task" in task_repr
        assert "id=1" in task_repr
        assert "Test task" in task_repr
        assert "pending" in task_repr