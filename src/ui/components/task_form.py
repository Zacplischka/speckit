"""
Task form component for new task creation.
"""

import streamlit as st
from typing import Callable, Optional
from src.ui.models import TaskFormData


class TaskFormComponent:
    """Component for task creation forms."""

    def render_task_form(
        self,
        form_data: TaskFormData,
        on_submit: Optional[Callable[[TaskFormData], bool]] = None,
        placeholder_text: str = "Enter task description..."
    ) -> bool:
        """
        Render task creation form.

        Args:
            form_data: Current form state
            on_submit: Callback for form submission
            placeholder_text: Placeholder for input field

        Returns:
            bool: True if form was submitted successfully
        """
        st.subheader("Add New Task")

        with st.form("add_task_form", clear_on_submit=True):
            # Task description input
            description = st.text_input(
                "Task Description",
                placeholder=placeholder_text,
                help="Enter a description for your new task (max 500 characters)"
            )

            # Submit button
            submitted = st.form_submit_button("Add Task", type="primary")

            # Handle form submission
            if submitted:
                form_data.description = description.strip()

                # Show validation errors if any
                if not form_data.validate():
                    st.error(form_data.error_message)
                    return False

                # Call the submit callback if provided
                if on_submit:
                    success = on_submit(form_data)
                    if success:
                        st.success("Task added successfully!")
                        # Clear form data for next submission
                        form_data.description = ""
                        form_data.error_message = None
                        form_data.is_valid = False
                        return True
                    else:
                        if form_data.error_message:
                            st.error(form_data.error_message)
                        else:
                            st.error("Failed to add task. Please try again.")
                        return False

        return False