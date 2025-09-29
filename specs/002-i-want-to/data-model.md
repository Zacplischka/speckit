# Data Model: Streamlit Task Management UI

## Core Entities

### Task (Existing Entity - No Changes)
**Purpose**: Represents a user-defined action item with lifecycle management

**Attributes**:
- `id: Optional[int]` - Unique identifier (None for new tasks, assigned by repository)
- `description: str` - Task description text (must not be empty)
- `status: TaskStatus` - Current task status ('pending' or 'completed')
- `created_at: datetime` - Task creation timestamp
- `completed_at: Optional[datetime]` - Task completion timestamp (None for pending tasks)

**Validation Rules**:
- Description cannot be empty or whitespace-only
- Pending tasks must have completed_at = None
- Completed tasks must have completed_at timestamp
- Status transitions: pending → completed (no reverse transition)

**State Transitions**:
```
[New Task] → pending → completed
```

### UI View State (New Entity)
**Purpose**: Manages current UI display mode and user interactions

**Attributes**:
- `current_view: ViewMode` - Active view ('active_tasks', 'completed_tasks', 'all_tasks')
- `selected_task_id: Optional[int]` - Currently selected task for operations
- `form_data: TaskFormData` - New task form state

**View Modes**:
- `active_tasks`: Display only pending tasks
- `completed_tasks`: Display only completed tasks
- `all_tasks`: Display all tasks with status indicators

### Task Form Data (New Entity)
**Purpose**: Captures user input for new task creation

**Attributes**:
- `description: str` - User-entered task description
- `is_valid: bool` - Whether form data passes validation
- `error_message: Optional[str]` - Validation error details

**Validation Rules**:
- Description must not be empty after stripping whitespace
- Description length should be reasonable (e.g., 1-500 characters)

## Repository Interface Extensions

### Existing Methods (No Changes)
- `create_task(description: str) -> Task`
- `mark_completed(task_id: int) -> bool`
- `get_all_tasks() -> List[Task]`
- `get_pending_tasks() -> List[Task]`
- `get_completed_tasks() -> List[Task]`
- `get_task_by_id(task_id: int) -> Optional[Task]`

### New Method Required
```python
def delete_task(self, task_id: int) -> bool:
    """
    Permanently delete a task from the database.

    Args:
        task_id: ID of task to delete

    Returns:
        bool: True if task was deleted, False if task not found

    Raises:
        RuntimeError: If database operation fails
    """
```

**SQL Implementation**:
```sql
DELETE FROM tasks WHERE id = ?
```

## UI Component Model

### Task Display Component
**Purpose**: Renders individual task with appropriate actions

**Properties**:
- `task: Task` - Task data to display
- `show_actions: bool` - Whether to show action buttons
- `view_mode: ViewMode` - Current view context

**Actions Available**:
- For pending tasks: [Mark Complete] [Delete]
- For completed tasks: [Delete]

### Task List Component
**Purpose**: Renders collection of tasks with filtering

**Properties**:
- `tasks: List[Task]` - Tasks to display
- `view_mode: ViewMode` - Current filter/view
- `empty_message: str` - Message when no tasks found

### Task Form Component
**Purpose**: Handles new task creation input

**Properties**:
- `form_data: TaskFormData` - Current form state
- `on_submit: Callable` - Form submission handler
- `placeholder_text: str` - Input field placeholder

## Database Schema (No Changes)

The existing SQLite schema remains unchanged:

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'completed')),
    created_at TEXT NOT NULL,
    completed_at TEXT
);
```

## Error Handling Model

### Repository Errors
- `ValueError`: Invalid input data (empty description, etc.)
- `RuntimeError`: Database operation failures
- `ConnectionError`: Database connection issues

### UI Error States
- Form validation errors (empty description)
- Network/database errors (show user-friendly message)
- No tasks found (show helpful empty state)

### Error Display Strategy
- Form errors: Inline validation messages
- Operation errors: Toast/alert notifications
- Empty states: Encouraging message with call-to-action