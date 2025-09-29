"""
Database connection management for SQLite database.
Provides connection utilities and configuration.
"""

import sqlite3
from typing import Optional


def get_connection(database_path: str) -> sqlite3.Connection:
    """
    Create and configure a SQLite database connection.

    Args:
        database_path: Path to SQLite database file or ":memory:" for in-memory DB

    Returns:
        sqlite3.Connection: Configured database connection

    Raises:
        sqlite3.Error: If connection cannot be established
    """
    try:
        # Create connection with row factory for easier data access
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row

        # Enable foreign key constraints (good practice)
        connection.execute("PRAGMA foreign_keys = ON")

        # Set journal mode for better performance and reliability
        connection.execute("PRAGMA journal_mode = WAL")

        # Set synchronous mode for better performance (still safe)
        connection.execute("PRAGMA synchronous = NORMAL")

        return connection

    except sqlite3.Error as e:
        raise sqlite3.Error(f"Failed to connect to database '{database_path}': {e}")


def close_connection(connection: Optional[sqlite3.Connection]) -> None:
    """
    Safely close a database connection.

    Args:
        connection: Database connection to close (can be None)
    """
    if connection:
        try:
            connection.close()
        except sqlite3.Error:
            # Log error in real application, ignore for this implementation
            pass