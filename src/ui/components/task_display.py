"""
Task display component for individual task rendering.
"""

import streamlit as st
from typing import Callable, Optional
from src.models.task import Task
from src.ui.models import ViewMode


class TaskDisplayComponent:
    """Component for displaying individual tasks with actions."""

    def render_task(
        self,
        task: Task,
        actions_enabled: bool = True,
        on_complete: Optional[Callable[[int], None]] = None,
        on_delete: Optional[Callable[[int], None]] = None,
        view_mode: ViewMode = ViewMode.ACTIVE_TASKS
    ) -> None:
        """
        Render a single task with optional actions.

        Args:
            task: Task to display
            actions_enabled: Whether to show action buttons
            on_complete: Callback for completing task
            on_delete: Callback for deleting task
            view_mode: Current view mode for context
        """
        with st.container():
            # Create columns for task content and actions
            if actions_enabled:
                task_col, action_col = st.columns([3, 1])
            else:
                task_col = st.container()
                action_col = None

            with task_col:
                # Display task description
                if task.status == 'completed':
                    # Show completed tasks with strikethrough effect
                    st.markdown(f"~~{task.description}~~")
                    st.caption(f"Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M')}")
                else:
                    st.write(task.description)
                    st.caption(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")

            # Action buttons
            if actions_enabled and action_col:
                with action_col:
                    if task.status == 'pending' and on_complete:
                        if st.button("✓ Complete", key=f"complete_{task.id}"):
                            on_complete(task.id)

                    if on_delete:
                        if st.button("🗑 Delete", key=f"delete_{task.id}"):
                            on_delete(task.id)

            # Add separator
            st.divider()