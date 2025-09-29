"""
Integration test for view filtering workflow.
This test MUST fail before implementation and pass after.
"""

import pytest
from datetime import datetime
from src.models.task import Task, TaskStatus
from src.database.repository import SQLiteTaskRepository


# Import UI components
from src.ui.controller import StreamlitUIController
from src.ui.models import ViewMode


class TestViewFilteringIntegration:
    """Integration tests for view filtering and switching workflow."""

    def setup_method(self):
        """Set up test environment with repository, controller, and diverse tasks."""
        self.repo = SQLiteTaskRepository(":memory:")
        self.controller = StreamlitUIController(self.repo)

        # Create tasks with different states and timestamps
        self.active_task1 = self.repo.create_task("Active task 1")
        self.active_task2 = self.repo.create_task("Active task 2")
        self.active_task3 = self.repo.create_task("Active task 3")

        self.completed_task1 = self.repo.create_task("Completed task 1")
        self.completed_task2 = self.repo.create_task("Completed task 2")

        # Mark some tasks as completed at different times
        self.repo.mark_completed(self.completed_task1.id)
        # Small delay to ensure different completion times
        import time
        time.sleep(0.01)
        self.repo.mark_completed(self.completed_task2.id)

    def test_active_tasks_view_filtering(self):
        """Test that active tasks view shows only pending tasks."""
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)

        # Should have exactly 3 active tasks
        assert len(active_tasks) == 3

        # All tasks should be pending
        for task in active_tasks:
            assert task.status == 'pending'
            assert task.completed_at is None

        # Should contain our specific active tasks
        active_task_ids = [t.id for t in active_tasks]
        assert self.active_task1.id in active_task_ids
        assert self.active_task2.id in active_task_ids
        assert self.active_task3.id in active_task_ids

        # Should NOT contain completed tasks
        assert self.completed_task1.id not in active_task_ids
        assert self.completed_task2.id not in active_task_ids

    def test_completed_tasks_view_filtering(self):
        """Test that completed tasks view shows only completed tasks."""
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)

        # Should have exactly 2 completed tasks
        assert len(completed_tasks) == 2

        # All tasks should be completed
        for task in completed_tasks:
            assert task.status == 'completed'
            assert task.completed_at is not None

        # Should contain our specific completed tasks
        completed_task_ids = [t.id for t in completed_tasks]
        assert self.completed_task1.id in completed_task_ids
        assert self.completed_task2.id in completed_task_ids

        # Should NOT contain active tasks
        assert self.active_task1.id not in completed_task_ids
        assert self.active_task2.id not in completed_task_ids
        assert self.active_task3.id not in completed_task_ids

    def test_all_tasks_view_shows_everything(self):
        """Test that all tasks view shows both pending and completed tasks."""
        all_tasks = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)

        # Should have all 5 tasks
        assert len(all_tasks) == 5

        # Should contain all our tasks
        all_task_ids = [t.id for t in all_tasks]
        assert self.active_task1.id in all_task_ids
        assert self.active_task2.id in all_task_ids
        assert self.active_task3.id in all_task_ids
        assert self.completed_task1.id in all_task_ids
        assert self.completed_task2.id in all_task_ids

        # Should have correct mix of statuses
        pending_count = sum(1 for task in all_tasks if task.status == 'pending')
        completed_count = sum(1 for task in all_tasks if task.status == 'completed')
        assert pending_count == 3
        assert completed_count == 2

    def test_view_switching_workflow(self):
        """Test the complete workflow of switching between different views."""
        # Start with active view
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 3

        # Switch to completed view
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks) == 2

        # Switch to all tasks view
        all_tasks = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        assert len(all_tasks) == 5

        # Switch back to active view
        active_tasks_again = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks_again) == 3

        # Verify data consistency across view switches
        active_ids = set(t.id for t in active_tasks)
        active_ids_again = set(t.id for t in active_tasks_again)
        assert active_ids == active_ids_again

    def test_view_filtering_after_task_state_changes(self):
        """Test that view filtering updates correctly after task state changes."""
        # Initial state verification
        active_tasks_before = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        completed_tasks_before = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(active_tasks_before) == 3
        assert len(completed_tasks_before) == 2

        # Mark one active task as completed
        completion_result = self.controller.complete_task(self.active_task1.id)
        assert completion_result is True

        # Verify active view has one less task
        active_tasks_after = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks_after) == 2
        active_ids_after = [t.id for t in active_tasks_after]
        assert self.active_task1.id not in active_ids_after

        # Verify completed view has one more task
        completed_tasks_after = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks_after) == 3
        completed_ids_after = [t.id for t in completed_tasks_after]
        assert self.active_task1.id in completed_ids_after

        # Verify all tasks view still has all tasks
        all_tasks_after = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        assert len(all_tasks_after) == 5

    def test_view_filtering_after_task_deletion(self):
        """Test that view filtering updates correctly after task deletion."""
        # Initial state verification
        active_tasks_before = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        all_tasks_before = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        assert len(active_tasks_before) == 3
        assert len(all_tasks_before) == 5

        # Delete one active task
        deletion_result = self.controller.delete_task(self.active_task1.id)
        assert deletion_result is True

        # Verify active view has one less task
        active_tasks_after = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks_after) == 2
        active_ids_after = [t.id for t in active_tasks_after]
        assert self.active_task1.id not in active_ids_after

        # Verify all tasks view has one less task
        all_tasks_after = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        assert len(all_tasks_after) == 4
        all_ids_after = [t.id for t in all_tasks_after]
        assert self.active_task1.id not in all_ids_after

        # Delete one completed task
        deletion_result2 = self.controller.delete_task(self.completed_task1.id)
        assert deletion_result2 is True

        # Verify completed view has one less task
        completed_tasks_after = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks_after) == 1
        completed_ids_after = [t.id for t in completed_tasks_after]
        assert self.completed_task1.id not in completed_ids_after

        # Verify all tasks view reflects both deletions
        all_tasks_final = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        assert len(all_tasks_final) == 3

    def test_empty_view_scenarios(self):
        """Test view filtering behavior when views are empty."""
        # Delete all active tasks
        active_task_ids = [self.active_task1.id, self.active_task2.id, self.active_task3.id]
        for task_id in active_task_ids:
            deletion_result = self.controller.delete_task(task_id)
            assert deletion_result is True

        # Verify active view is empty
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        assert len(active_tasks) == 0

        # Verify completed view still has tasks
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        assert len(completed_tasks) == 2

        # Delete all completed tasks
        completed_task_ids = [self.completed_task1.id, self.completed_task2.id]
        for task_id in completed_task_ids:
            deletion_result = self.controller.delete_task(task_id)
            assert deletion_result is True

        # Verify all views are empty
        active_tasks_empty = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        completed_tasks_empty = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        all_tasks_empty = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)

        assert len(active_tasks_empty) == 0
        assert len(completed_tasks_empty) == 0
        assert len(all_tasks_empty) == 0

    def test_view_filtering_with_large_dataset(self):
        """Test view filtering performance and correctness with larger dataset."""
        # Create many more tasks
        additional_active_tasks = []
        additional_completed_tasks = []

        # Add 20 more active tasks
        for i in range(20):
            task = self.repo.create_task(f"Additional active task {i+1}")
            additional_active_tasks.append(task)

        # Add 15 more completed tasks
        for i in range(15):
            task = self.repo.create_task(f"Additional completed task {i+1}")
            self.repo.mark_completed(task.id)
            additional_completed_tasks.append(task)

        # Test filtering with larger dataset
        active_tasks = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        completed_tasks = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        all_tasks = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)

        # Verify counts
        assert len(active_tasks) == 23  # 3 original + 20 additional
        assert len(completed_tasks) == 17  # 2 original + 15 additional
        assert len(all_tasks) == 40  # Total of all tasks

        # Verify all active tasks are actually pending
        for task in active_tasks:
            assert task.status == 'pending'

        # Verify all completed tasks are actually completed
        for task in completed_tasks:
            assert task.status == 'completed'

    def test_view_filtering_data_integrity(self):
        """Test that view filtering maintains data integrity across operations."""
        # Get initial snapshots
        initial_active = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        initial_completed = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        initial_all = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)

        # Verify data integrity
        assert len(initial_active) + len(initial_completed) == len(initial_all)

        # Perform multiple operations
        self.controller.complete_task(self.active_task1.id)
        self.controller.delete_task(self.active_task2.id)

        # Get updated snapshots
        updated_active = self.controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
        updated_completed = self.controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
        updated_all = self.controller.get_tasks_for_view(ViewMode.ALL_TASKS)

        # Verify updated integrity
        assert len(updated_active) + len(updated_completed) == len(updated_all)

        # Verify no task appears in multiple status categories
        active_ids = set(t.id for t in updated_active)
        completed_ids = set(t.id for t in updated_completed)
        assert len(active_ids.intersection(completed_ids)) == 0

        # Verify all tasks in all_view are properly categorized
        all_ids = set(t.id for t in updated_all)
        assert active_ids.union(completed_ids) == all_ids