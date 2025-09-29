"""
Repository Extension Contract for Task Deletion
Defines the additional method needed for the existing TaskRepository.
"""

from abc import ABC, abstractmethod


class TaskRepositoryExtension(ABC):
    """
    Extension to the existing TaskRepository interface.
    Adds task deletion capability required by the UI.
    """

    @abstractmethod
    def delete_task(self, task_id: int) -> bool:
        """
        Permanently delete a task from the database.

        This method removes a task completely from storage. Unlike marking
        a task as completed, this operation is irreversible.

        Args:
            task_id: Unique identifier of the task to delete

        Returns:
            bool: True if the task was successfully deleted, False if the
                  task was not found or could not be deleted

        Raises:
            RuntimeError: If the database operation fails due to connection
                         issues, constraint violations, or other database errors

        Example:
            >>> repository = SQLiteTaskRepository("tasks.db")
            >>> task = repository.create_task("Sample task")
            >>> success = repository.delete_task(task.id)
            >>> assert success == True

        SQL Implementation:
            DELETE FROM tasks WHERE id = ?

        Database Considerations:
            - Uses WHERE clause to target specific task by ID
            - Returns rowcount to determine if task existed
            - Handles transaction rollback on errors
            - No cascade deletes needed (no foreign key relationships)

        UI Integration:
            - Called when user clicks "Delete" button on task
            - Should be followed by UI refresh to show updated task list
            - Error handling should display user-friendly messages
        """
        pass