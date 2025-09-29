"""
Database schema migrations and initialization.
Creates tables and indexes as defined in data-model.md.
"""

import sqlite3
from typing import Optional


def create_schema(connection: sqlite3.Connection) -> None:
    """
    Create the database schema for the to-do application.

    Args:
        connection: SQLite database connection

    Raises:
        sqlite3.Error: If schema creation fails
    """
    try:
        cursor = connection.cursor()

        # Create tasks table with constraints from data-model.md
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL CHECK(length(description) > 0),
                status TEXT NOT NULL CHECK(status IN ('pending', 'completed')),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                CONSTRAINT valid_completion CHECK (
                    (status = 'pending' AND completed_at IS NULL) OR
                    (status = 'completed' AND completed_at IS NOT NULL)
                )
            )
        """)

        # Create indexes for performance as specified in data-model.md
        create_indexes(cursor)

        # Commit the schema changes
        connection.commit()

    except sqlite3.Error as e:
        connection.rollback()
        raise sqlite3.Error(f"Failed to create schema: {e}")


def create_indexes(cursor: sqlite3.Cursor) -> None:
    """
    Create database indexes for optimized queries.

    Args:
        cursor: SQLite database cursor

    Raises:
        sqlite3.Error: If index creation fails
    """
    # Index for filtering by status (common query pattern)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_status
        ON tasks(status)
    """)

    # Index for ordering by creation time
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_created_at
        ON tasks(created_at)
    """)

    # Index for querying completed tasks by completion time
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_tasks_completed_at
        ON tasks(completed_at)
        WHERE completed_at IS NOT NULL
    """)


def drop_schema(connection: sqlite3.Connection) -> None:
    """
    Drop all tables and indexes (for testing purposes).

    Args:
        connection: SQLite database connection

    Raises:
        sqlite3.Error: If schema dropping fails
    """
    try:
        cursor = connection.cursor()

        # Drop indexes first
        cursor.execute("DROP INDEX IF EXISTS idx_tasks_completed_at")
        cursor.execute("DROP INDEX IF EXISTS idx_tasks_created_at")
        cursor.execute("DROP INDEX IF EXISTS idx_tasks_status")

        # Drop tables
        cursor.execute("DROP TABLE IF EXISTS tasks")

        connection.commit()

    except sqlite3.Error as e:
        connection.rollback()
        raise sqlite3.Error(f"Failed to drop schema: {e}")


def get_schema_version(connection: sqlite3.Connection) -> Optional[str]:
    """
    Get the current schema version (for future migrations).

    Args:
        connection: SQLite database connection

    Returns:
        Optional[str]: Schema version or None if not set
    """
    try:
        cursor = connection.cursor()

        # Check if tasks table exists as a simple version check
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='tasks'
        """)

        if cursor.fetchone():
            return "1.0.0"  # Current version
        else:
            return None  # No schema

    except sqlite3.Error:
        return None