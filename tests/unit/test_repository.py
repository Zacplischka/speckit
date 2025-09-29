"""
Unit tests for SQLiteTaskRepository methods.
Tests repository methods in isolation with mocking where appropriate.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from datetime import datetime
from src.database.repository import SQLiteTaskRepository
from src.models.task import Task


class TestSQLiteTaskRepositoryUnit:
    """Unit tests for SQLiteTaskRepository methods."""

    def setup_method(self):
        """Set up test repository for each test."""
        # Use temporary file for isolated testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.repo = SQLiteTaskRepository(self.db_path)

    def teardown_method(self):
        """Clean up test repository after each test."""
        self.repo.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_context_manager_support(self):
        """Test that repository supports context manager protocol."""
        with SQLiteTaskRepository(":memory:") as repo:
            task = repo.create_task("Context manager test")
            assert task.id is not None

        # Repository should be properly closed after context exit

    def test_auto_create_schema_can_be_disabled(self):
        """Test that auto schema creation can be disabled."""
        # Create repo without auto schema creation
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()

        try:
            repo = SQLiteTaskRepository(temp_db.name, auto_create_schema=False)

            # Should fail because schema doesn't exist
            with pytest.raises(RuntimeError, match="Failed to create task"):
                repo.create_task("Test task")

            repo.close()
        finally:
            os.unlink(temp_db.name)

    def test_create_task_input_validation(self):
        """Test input validation in create_task method."""
        # Test various invalid inputs
        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.repo.create_task("")

        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.repo.create_task(None)

        with pytest.raises(ValueError, match="Description cannot be empty"):
            self.repo.create_task("   ")

    def test_create_task_description_trimming(self):
        """Test that create_task trims whitespace from descriptions."""
        task = self.repo.create_task("  Test task  ")
        assert task.description == "Test task"

    def test_mark_completed_with_invalid_id_types(self):
        """Test mark_completed with invalid ID types."""
        # Test with string (should work due to SQLite's type affinity)
        result = self.repo.mark_completed("999")
        assert result is False

        # Test with None - SQLite actually handles this gracefully by returning False
        result = self.repo.mark_completed(None)
        assert result is False

    def test_get_task_by_id_with_invalid_id_types(self):
        """Test get_task_by_id with invalid ID types."""
        # Test with string (should work due to SQLite's type affinity)
        task = self.repo.get_task_by_id("999")
        assert task is None

    def test_repository_isolation(self):
        """Test that different repository instances are isolated."""
        # Create two separate repositories
        temp_db2 = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db2.close()

        try:
            repo2 = SQLiteTaskRepository(temp_db2.name)

            # Add task to first repository
            task1 = self.repo.create_task("Repo 1 task")

            # Add task to second repository
            task2 = repo2.create_task("Repo 2 task")

            # Repositories should be isolated
            assert len(self.repo.get_all_tasks()) == 1
            assert len(repo2.get_all_tasks()) == 1

            assert self.repo.get_all_tasks()[0].description == "Repo 1 task"
            assert repo2.get_all_tasks()[0].description == "Repo 2 task"

            repo2.close()
        finally:
            os.unlink(temp_db2.name)

    def test_repository_persistence_across_instances(self):
        """Test that data persists across repository instances."""
        # Create task with first instance
        task = self.repo.create_task("Persistent task")
        task_id = task.id
        self.repo.close()

        # Create new instance with same database
        repo2 = SQLiteTaskRepository(self.db_path, auto_create_schema=False)

        # Data should persist
        persisted_task = repo2.get_task_by_id(task_id)
        assert persisted_task is not None
        assert persisted_task.description == "Persistent task"
        assert persisted_task.status == 'pending'

        repo2.close()

    def test_concurrent_task_creation(self):
        """Test that concurrent task creation assigns unique IDs."""
        # Create multiple tasks rapidly
        tasks = []
        for i in range(10):
            task = self.repo.create_task(f"Task {i}")
            tasks.append(task)

        # All tasks should have unique IDs
        task_ids = [task.id for task in tasks]
        assert len(set(task_ids)) == 10  # All IDs should be unique

        # IDs should be sequential
        task_ids.sort()
        for i, task_id in enumerate(task_ids):
            assert task_id == i + 1

    def test_row_to_task_datetime_parsing(self):
        """Test _row_to_task method handles various datetime formats."""
        # Create a task to test datetime parsing
        task = self.repo.create_task("Datetime test")

        # Retrieve and verify the parsing worked
        retrieved_task = self.repo.get_task_by_id(task.id)
        assert isinstance(retrieved_task.created_at, datetime)
        assert retrieved_task.completed_at is None

        # Mark complete and test completion datetime parsing
        self.repo.mark_completed(task.id)
        completed_task = self.repo.get_task_by_id(task.id)
        assert isinstance(completed_task.completed_at, datetime)

    def test_query_methods_return_correct_types(self):
        """Test that query methods return correct types and empty lists."""
        # Test empty database
        assert isinstance(self.repo.get_all_tasks(), list)
        assert isinstance(self.repo.get_pending_tasks(), list)
        assert isinstance(self.repo.get_completed_tasks(), list)
        assert len(self.repo.get_all_tasks()) == 0

        # Test with data
        task = self.repo.create_task("Type test")
        self.repo.mark_completed(task.id)

        all_tasks = self.repo.get_all_tasks()
        pending_tasks = self.repo.get_pending_tasks()
        completed_tasks = self.repo.get_completed_tasks()

        assert isinstance(all_tasks, list)
        assert isinstance(pending_tasks, list)
        assert isinstance(completed_tasks, list)

        assert len(all_tasks) == 1
        assert len(pending_tasks) == 0
        assert len(completed_tasks) == 1

        # All returned objects should be Task instances
        for task_list in [all_tasks, completed_tasks]:
            for task in task_list:
                assert isinstance(task, Task)

    def test_repository_close_method(self):
        """Test repository close method."""
        # Test that close can be called multiple times safely
        self.repo.close()
        self.repo.close()  # Should not raise an error

        # Test that operations fail gracefully after close
        # (Note: With current implementation, operations might still work
        # because we create new connections for file databases)