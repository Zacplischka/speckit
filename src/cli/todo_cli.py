"""
Command-line interface for testing the to-do database layer.
Provides basic CRUD operations for manual testing and validation.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from src.database.connection import get_connection
from src.database.migrations import create_schema
from src.database.repository import SQLiteTaskRepository


def setup_database(db_path: str) -> SQLiteTaskRepository:
    """
    Initialize database and return repository instance.

    Args:
        db_path: Path to SQLite database file

    Returns:
        SQLiteTaskRepository: Configured repository instance
    """
    # Ensure database directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # Initialize database schema
    connection = get_connection(db_path)
    create_schema(connection)
    connection.close()

    return SQLiteTaskRepository(db_path)


def list_tasks(repo: SQLiteTaskRepository, status_filter: str = None) -> None:
    """List tasks with optional status filter."""
    if status_filter == "pending":
        tasks = repo.get_pending_tasks()
        print("Pending Tasks:")
    elif status_filter == "completed":
        tasks = repo.get_completed_tasks()
        print("Completed Tasks:")
    else:
        tasks = repo.get_all_tasks()
        print("All Tasks:")

    if not tasks:
        print("  No tasks found.")
        return

    for task in tasks:
        status_indicator = "✓" if task.status == "completed" else "○"
        created = task.created_at.strftime("%Y-%m-%d %H:%M")

        if task.completed_at:
            completed = task.completed_at.strftime("%Y-%m-%d %H:%M")
            print(f"  {status_indicator} [{task.id}] {task.description} (created: {created}, completed: {completed})")
        else:
            print(f"  {status_indicator} [{task.id}] {task.description} (created: {created})")


def add_task(repo: SQLiteTaskRepository, description: str) -> None:
    """Add a new task."""
    try:
        task = repo.create_task(description)
        print(f"Created task {task.id}: {task.description}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def complete_task(repo: SQLiteTaskRepository, task_id: int) -> None:
    """Mark a task as completed."""
    success = repo.mark_completed(task_id)
    if success:
        print(f"Task {task_id} marked as completed.")
    else:
        print(f"Failed to complete task {task_id}. Task may not exist or is already completed.", file=sys.stderr)
        sys.exit(1)


def show_task(repo: SQLiteTaskRepository, task_id: int) -> None:
    """Show details of a specific task."""
    task = repo.get_task_by_id(task_id)
    if not task:
        print(f"Task {task_id} not found.", file=sys.stderr)
        sys.exit(1)

    status_indicator = "✓" if task.status == "completed" else "○"
    created = task.created_at.strftime("%Y-%m-%d %H:%M:%S")

    print(f"Task {task.id}:")
    print(f"  {status_indicator} {task.description}")
    print(f"  Status: {task.status}")
    print(f"  Created: {created}")

    if task.completed_at:
        completed = task.completed_at.strftime("%Y-%m-%d %H:%M:%S")
        print(f"  Completed: {completed}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="To-Do Database Layer CLI")
    parser.add_argument("--db", default="data/todos.db", help="Database file path")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--status", choices=["pending", "completed"], help="Filter by status")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("description", help="Task description")

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark task as completed")
    complete_parser.add_argument("id", type=int, help="Task ID")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show task details")
    show_parser.add_argument("id", type=int, help="Task ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Setup database and repository
    try:
        repo = setup_database(args.db)
    except Exception as e:
        print(f"Failed to initialize database: {e}", file=sys.stderr)
        sys.exit(1)

    # Execute command
    try:
        if args.command == "list":
            list_tasks(repo, args.status)
        elif args.command == "add":
            add_task(repo, args.description)
        elif args.command == "complete":
            complete_task(repo, args.id)
        elif args.command == "show":
            show_task(repo, args.id)
    except Exception as e:
        print(f"Command failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()