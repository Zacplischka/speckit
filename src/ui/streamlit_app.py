"""
Main Streamlit application for task management.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from src.database.repository import SQLiteTaskRepository
from src.ui.controller import StreamlitUIController
from src.ui.models import ViewMode, UIState
from src.ui.components.task_list import TaskListComponent
from src.ui.components.task_form import TaskFormComponent


# App configuration
st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize session state with repository and UI state."""
    if 'repository' not in st.session_state:
        # Use a persistent database file
        st.session_state.repository = SQLiteTaskRepository("tasks.db")

    if 'controller' not in st.session_state:
        st.session_state.controller = StreamlitUIController(st.session_state.repository)

    if 'ui_state' not in st.session_state:
        st.session_state.ui_state = UIState()

    if 'task_list' not in st.session_state:
        st.session_state.task_list = TaskListComponent()

    if 'task_form' not in st.session_state:
        st.session_state.task_form = TaskFormComponent()


def render_sidebar():
    """Render sidebar with view selection."""
    st.sidebar.title("📋 Task Manager")
    st.sidebar.markdown("---")

    # View selection
    st.sidebar.subheader("Views")

    view_options = {
        "Active Tasks": ViewMode.ACTIVE_TASKS,
        "Completed Tasks": ViewMode.COMPLETED_TASKS,
        "All Tasks": ViewMode.ALL_TASKS
    }

    # Create radio buttons for view selection
    selected_view_name = st.sidebar.radio(
        "Select View",
        options=list(view_options.keys()),
        index=0 if st.session_state.ui_state.current_view == ViewMode.ACTIVE_TASKS
              else 1 if st.session_state.ui_state.current_view == ViewMode.COMPLETED_TASKS
              else 2
    )

    # Update UI state if view changed
    new_view_mode = view_options[selected_view_name]
    if new_view_mode != st.session_state.ui_state.current_view:
        st.session_state.ui_state.current_view = new_view_mode
        st.rerun()

    st.sidebar.markdown("---")

    # Statistics
    st.sidebar.subheader("Statistics")
    try:
        all_tasks = st.session_state.controller.get_tasks_for_view(ViewMode.ALL_TASKS)
        active_count = len([t for t in all_tasks if t.status == 'pending'])
        completed_count = len([t for t in all_tasks if t.status == 'completed'])

        st.sidebar.metric("Active Tasks", active_count)
        st.sidebar.metric("Completed Tasks", completed_count)
        st.sidebar.metric("Total Tasks", len(all_tasks))
    except Exception as e:
        st.sidebar.error(f"Error loading statistics: {e}")


def handle_task_complete(task_id: int):
    """Handle task completion."""
    try:
        success = st.session_state.controller.complete_task(task_id)
        if success:
            st.success("Task marked as completed!")
            st.rerun()
        else:
            st.error("Failed to complete task.")
    except Exception as e:
        st.error(f"Error completing task: {e}")


def handle_task_delete(task_id: int):
    """Handle task deletion."""
    try:
        success = st.session_state.controller.delete_task(task_id)
        if success:
            st.success("Task deleted!")
            st.rerun()
        else:
            st.error("Failed to delete task.")
    except Exception as e:
        st.error(f"Error deleting task: {e}")


def handle_task_create(form_data):
    """Handle new task creation."""
    try:
        return st.session_state.controller.create_new_task(form_data)
    except Exception as e:
        form_data.error_message = f"Error creating task: {e}"
        return False


def get_empty_message(view_mode: ViewMode) -> str:
    """Get appropriate empty message for current view."""
    if view_mode == ViewMode.ACTIVE_TASKS:
        return "No active tasks. Add one below!"
    elif view_mode == ViewMode.COMPLETED_TASKS:
        return "No completed tasks yet."
    else:
        return "No tasks found. Add your first task below!"


def main():
    """Main application function."""
    initialize_session_state()

    # Render sidebar
    render_sidebar()

    # Main content area
    st.title("📋 Task Manager")

    current_view = st.session_state.ui_state.current_view

    # Get tasks for current view
    try:
        tasks = st.session_state.controller.get_tasks_for_view(current_view)
    except Exception as e:
        st.error(f"Error loading tasks: {e}")
        return

    # Render task list
    st.session_state.task_list.render_task_list(
        tasks=tasks,
        view_mode=current_view,
        on_complete=handle_task_complete,
        on_delete=handle_task_delete,
        empty_message=get_empty_message(current_view)
    )

    st.markdown("---")

    # Render task creation form (always visible)
    st.session_state.task_form.render_task_form(
        form_data=st.session_state.ui_state.form_data,
        on_submit=handle_task_create,
        placeholder_text="What needs to be done?"
    )


if __name__ == "__main__":
    main()