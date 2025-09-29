"""
Task list component for rendering collections of tasks.
"""

import streamlit as st
from typing import List, Callable, Optional
from src.models.task import Task
from src.ui.models import ViewMode
from src.ui.components.task_display import TaskDisplayComponent


class TaskListComponent:
    """Component for rendering lists of tasks with filtering."""

    def __init__(self):
        self.task_display = TaskDisplayComponent()

    def render_task_list(
        self,
        tasks: List[Task],
        view_mode: ViewMode,
        on_complete: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        empty_message: str = "No tasks found."
    ) -> None:
        """
        Render a list of tasks with appropriate filtering.

        Args:
            tasks: List of tasks to display
            view_mode: Current view mode for context
            on_complete: Callback for completing task
            on_delete: Callback for deleting task
            empty_message: Message to show when no tasks
        """
        if not tasks:
            st.info(empty_message)
            return

        # Add task count header
        task_count = len(tasks)
        if view_mode == ViewMode.ACTIVE_TASKS:
            st.subheader(f"Active Tasks ({task_count})")
        elif view_mode == ViewMode.COMPLETED_TASKS:
            st.subheader(f"Completed Tasks ({task_count})")
        else:
            active_count = sum(1 for task in tasks if task.status == 'pending')
            completed_count = sum(1 for task in tasks if task.status == 'completed')
            st.subheader(f"All Tasks ({task_count}) - {active_count} active, {completed_count} completed")

        # Render each task
        for task in tasks:
            self.task_display.render_task(
                task=task,
                actions_enabled=True,
                on_complete=on_complete,
                on_delete=on_delete,
                view_mode=view_mode
            )