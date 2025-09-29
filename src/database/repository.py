"""
SQLite implementation of TaskRepository interface.
Implements all abstract methods from contracts/task_repository.py.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from src.models.task import Task, TaskStatus
from src.database.connection import get_connection, close_connection
from src.database.migrations import create_schema


class SQLiteTaskRepository:
    """
    SQLite implementation of TaskRepository interface.

    Provides persistent storage for tasks using SQLite database
    with full ACID compliance and constraint enforcement.
    """

    def __init__(self, database_path: str, auto_create_schema: bool = True):
        """
        Initialize repository with database path.

        Args:
            database_path: Path to SQLite database file or ":memory:" for in-memory DB
            auto_create_schema: Whether to automatically create schema if it doesn't exist
        """
        self.database_path = database_path
        self._connection = None

        # For in-memory databases, keep a persistent connection
        if database_path == ":memory:":
            self._connection = get_connection(database_path)

        if auto_create_schema:
            self._ensure_schema_exists()

    def close(self) -> None:
        """
        Close the repository and clean up resources.
        Call this when done with the repository to ensure proper cleanup.
        """
        if self._connection:
            close_connection(self._connection)
            self._connection = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a configured database connection."""
        if self._connection:
            return self._connection
        return get_connection(self.database_path)

    def _ensure_schema_exists(self) -> None:
        """Ensure database schema exists."""
        connection = self._get_connection()
        try:
            create_schema(connection)
        finally:
            # Don't close persistent connections
            if not self._connection:
                close_connection(connection)

    def create_task(self, description: str) -> Task:
        """
        Create a new task with pending status.

        Args:
            description: Task description text (must not be empty)

        Returns:
            Task: Created task with assigned ID and timestamps

        Raises:
            ValueError: If description is empty or None
        """
        # Validate description before database operation
        if not description or not description.strip():
            raise ValueError("Description cannot be empty")

        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            # Insert new task using SQL pattern from data-model.md
            cursor.execute("""
                INSERT INTO tasks (description, status, created_at)
                VALUES (?, 'pending', CURRENT_TIMESTAMP)
            """, (description.strip(),))

            # Get the assigned ID
            task_id = cursor.lastrowid

            # Retrieve the created task to get exact timestamp
            cursor.execute("""
                SELECT id, description, status, created_at, completed_at
                FROM tasks
                WHERE id = ?
            """, (task_id,))

            row = cursor.fetchone()
            connection.commit()

            # Convert database row to Task object
            return Task(
                id=row['id'],
                description=row['description'],
                status=row['status'],
                created_at=datetime.fromisoformat(row['created_at']),
                completed_at=None
            )

        except sqlite3.Error as e:
            connection.rollback()
            raise RuntimeError(f"Failed to create task: {e}")
        finally:
            if not self._connection:
                close_connection(connection)

    def mark_completed(self, task_id: int) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: ID of task to mark complete

        Returns:
            bool: True if task was marked complete, False if task not found or already complete
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            # Update task using SQL pattern from data-model.md
            cursor.execute("""
                UPDATE tasks
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'pending'
            """, (task_id,))

            rows_affected = cursor.rowcount
            connection.commit()

            # Return True if exactly one row was updated
            return rows_affected == 1

        except sqlite3.Error as e:
            connection.rollback()
            raise RuntimeError(f"Failed to mark task completed: {e}")
        finally:
            if not self._connection:
                close_connection(connection)

    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks ordered by creation time (newest first).

        Returns:
            List[Task]: All tasks in the system
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            # Query all tasks using SQL pattern from data-model.md
            cursor.execute("""
                SELECT id, description, status, created_at, completed_at
                FROM tasks
                ORDER BY created_at DESC
            """)

            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]

        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve all tasks: {e}")
        finally:
            if not self._connection:
                close_connection(connection)

    def get_pending_tasks(self) -> List[Task]:
        """
        Retrieve only pending tasks ordered by creation time (newest first).

        Returns:
            List[Task]: All pending tasks
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            # Query pending tasks using SQL pattern from data-model.md
            cursor.execute("""
                SELECT id, description, status, created_at, completed_at
                FROM tasks
                WHERE status = 'pending'
                ORDER BY created_at DESC
            """)

            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]

        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve pending tasks: {e}")
        finally:
            if not self._connection:
                close_connection(connection)

    def get_completed_tasks(self) -> List[Task]:
        """
        Retrieve only completed tasks ordered by completion time (newest first).

        Returns:
            List[Task]: All completed tasks
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            # Query completed tasks using SQL pattern from data-model.md
            cursor.execute("""
                SELECT id, description, status, created_at, completed_at
                FROM tasks
                WHERE status = 'completed'
                ORDER BY completed_at DESC
            """)

            rows = cursor.fetchall()
            return [self._row_to_task(row) for row in rows]

        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve completed tasks: {e}")
        finally:
            if not self._connection:
                close_connection(connection)

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Retrieve a specific task by ID.

        Args:
            task_id: ID of task to retrieve

        Returns:
            Optional[Task]: Task if found, None otherwise
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT id, description, status, created_at, completed_at
                FROM tasks
                WHERE id = ?
            """, (task_id,))

            row = cursor.fetchone()
            return self._row_to_task(row) if row else None

        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to retrieve task by ID: {e}")
        finally:
            if not self._connection:
                close_connection(connection)

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
        """
        connection = self._get_connection()
        try:
            cursor = connection.cursor()

            # Delete task using SQL pattern from contract
            cursor.execute("""
                DELETE FROM tasks WHERE id = ?
            """, (task_id,))

            rows_affected = cursor.rowcount
            connection.commit()

            # Return True if exactly one row was deleted
            return rows_affected == 1

        except sqlite3.Error as e:
            connection.rollback()
            raise RuntimeError(f"Failed to delete task: {e}")
        finally:
            if not self._connection:
                close_connection(connection)

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """
        Convert database row to Task object.

        Args:
            row: SQLite row object

        Returns:
            Task: Task object with proper type conversion
        """
        # Handle SQLite datetime format
        created_at_str = row['created_at']
        if created_at_str.endswith('Z'):
            created_at = datetime.fromisoformat(created_at_str[:-1])
        elif 'T' in created_at_str:
            created_at = datetime.fromisoformat(created_at_str)
        else:
            # SQLite CURRENT_TIMESTAMP format: "YYYY-MM-DD HH:MM:SS"
            created_at = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S')

        completed_at = None
        if row['completed_at']:
            completed_at_str = row['completed_at']
            if completed_at_str.endswith('Z'):
                completed_at = datetime.fromisoformat(completed_at_str[:-1])
            elif 'T' in completed_at_str:
                completed_at = datetime.fromisoformat(completed_at_str)
            else:
                completed_at = datetime.strptime(completed_at_str, '%Y-%m-%d %H:%M:%S')

        return Task(
            id=row['id'],
            description=row['description'],
            status=row['status'],
            created_at=created_at,
            completed_at=completed_at
        )