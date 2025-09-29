"""
Integration tests for complete user scenarios from quickstart.md.
These tests MUST fail before implementation and pass after.
"""

import pytest
import tempfile
import os
from src.database.connection import get_connection
from src.database.migrations import create_schema
from src.database.repository import SQLiteTaskRepository


class TestBasicTaskLifecycle:
    """Integration test for basic task lifecycle scenario from quickstart.md."""

    def setup_method(self):
        """Set up test database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Initialize database with schema
        connection = get_connection(self.db_path)
        create_schema(connection)
        connection.close()

        # Create repository instance
        self.repo = SQLiteTaskRepository(self.db_path)

    def teardown_method(self):
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_complete_scenario_1_basic_task_lifecycle(self):
        """Test complete Scenario 1: Basic Task Lifecycle from quickstart.md."""
        # Given: Empty database
        assert len(self.repo.get_all_tasks()) == 0

        # When: Create a task
        task = self.repo.create_task("Test task")

        # Then: Task exists and is pending
        assert task.id is not None
        assert task.status == 'pending'
        assert task.completed_at is None
        assert len(self.repo.get_pending_tasks()) == 1

        # When: Mark task complete
        success = self.repo.mark_completed(task.id)

        # Then: Task is completed
        assert success is True
        completed_task = self.repo.get_task_by_id(task.id)
        assert completed_task.status == 'completed'
        assert completed_task.completed_at is not None
        assert len(self.repo.get_completed_tasks()) == 1
        assert len(self.repo.get_pending_tasks()) == 0

    def test_database_persistence_across_operations(self):
        """Test database persistence across operations."""
        # Create tasks
        task1 = self.repo.create_task("Persistent task 1")
        task2 = self.repo.create_task("Persistent task 2")

        # Mark one complete
        self.repo.mark_completed(task1.id)

        # Create new repository instance (simulates app restart)
        new_repo = SQLiteTaskRepository(self.db_path)

        # Verify data persisted
        all_tasks = new_repo.get_all_tasks()
        assert len(all_tasks) == 2

        pending_tasks = new_repo.get_pending_tasks()
        assert len(pending_tasks) == 1
        assert pending_tasks[0].id == task2.id

        completed_tasks = new_repo.get_completed_tasks()
        assert len(completed_tasks) == 1
        assert completed_tasks[0].id == task1.id

    def test_proper_timestamps_and_status_transitions(self):
        """Test proper timestamps and status transitions."""
        # Create task
        task = self.repo.create_task("Timestamp test")
        original_created_at = task.created_at

        # Verify initial state
        assert task.status == 'pending'
        assert task.completed_at is None
        assert task.created_at is not None

        # Add delay to ensure different timestamp
        import time
        time.sleep(1)

        # Mark complete
        self.repo.mark_completed(task.id)

        # Verify final state
        completed_task = self.repo.get_task_by_id(task.id)
        assert completed_task.status == 'completed'
        assert completed_task.completed_at is not None
        assert completed_task.created_at == original_created_at
        assert completed_task.completed_at >= completed_task.created_at


class TestEdgeCases:
    """Integration test for edge cases scenario from quickstart.md."""

    def setup_method(self):
        """Set up test database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

        # Initialize database with schema
        connection = get_connection(self.db_path)
        create_schema(connection)
        connection.close()

        # Create repository instance
        self.repo = SQLiteTaskRepository(self.db_path)

    def teardown_method(self):
        """Clean up test database after each test."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_double_completion_attempts(self):
        """Test double completion attempts."""
        # Create and complete task
        task = self.repo.create_task("Double completion test")
        first_completion = self.repo.mark_completed(task.id)
        assert first_completion is True

        # Attempt second completion
        second_completion = self.repo.mark_completed(task.id)
        assert second_completion is False

        # Verify task is still completed (not corrupted)
        completed_task = self.repo.get_task_by_id(task.id)
        assert completed_task.status == 'completed'
        assert completed_task.completed_at is not None

    def test_invalid_task_ids(self):
        """Test invalid task IDs."""
        # Test with non-existent ID
        invalid_completion = self.repo.mark_completed(99999)
        assert invalid_completion is False

        # Test get_task_by_id with invalid ID
        invalid_task = self.repo.get_task_by_id(99999)
        assert invalid_task is None

    def test_empty_descriptions(self):
        """Test empty descriptions (should raise ValueError)."""
        # Test empty string
        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.repo.create_task("")

        # Test None
        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.repo.create_task(None)

        # Test whitespace-only (should also be invalid)
        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.repo.create_task("   ")

    def test_database_constraints_enforcement(self):
        """Test database constraints enforcement."""
        # Create task
        task = self.repo.create_task("Constraint test")

        # Verify constraint: pending tasks have no completion time
        pending_task = self.repo.get_task_by_id(task.id)
        assert pending_task.status == 'pending'
        assert pending_task.completed_at is None

        # Complete task
        self.repo.mark_completed(task.id)

        # Verify constraint: completed tasks have completion time
        completed_task = self.repo.get_task_by_id(task.id)
        assert completed_task.status == 'completed'
        assert completed_task.completed_at is not None

    def test_query_empty_database(self):
        """Test querying empty database returns empty results."""
        # Test all query methods on empty database
        assert len(self.repo.get_all_tasks()) == 0
        assert len(self.repo.get_pending_tasks()) == 0
        assert len(self.repo.get_completed_tasks()) == 0
        assert self.repo.get_task_by_id(1) is None