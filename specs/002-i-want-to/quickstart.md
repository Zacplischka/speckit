# Quickstart: Streamlit Task Management UI

## Prerequisites

1. Python 3.13+ installed
2. Existing speckit project with database layer (001-a-database-layer)
3. Working directory: project root (`/Users/zac/Desktop/Projects/speckit`)

## Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
pip install streamlit
```

### Step 2: Launch the Application
```bash
streamlit run src/ui/streamlit_app.py
```

### Step 3: Open in Browser
- Streamlit will automatically open http://localhost:8501
- If not, navigate to the URL shown in terminal

### Step 4: Test Basic Functionality
1. **Add a Task**: Enter "Buy groceries" and click "Add Task"
2. **Mark Complete**: Click "✓ Complete" button next to your task
3. **View Completed**: Use sidebar to switch to "Completed Tasks"
4. **Delete Task**: Click "🗑 Delete" button to remove task permanently

## Application Structure

```
src/ui/streamlit_app.py          # Main Streamlit application
├── TaskRepository integration   # Uses existing database layer
├── UI State management         # Session state for persistence
└── Component rendering         # Forms, lists, and actions
```

## Expected User Experience

### Initial Load
- Clean, minimal interface loads
- Sidebar shows "Active Tasks" view by default
- Empty state message: "No active tasks. Add one below!"
- Simple form at bottom for adding new tasks

### Adding Tasks
1. Type task description in text input
2. Click "Add Task" button or press Enter
3. Task appears immediately in active tasks list
4. Form clears for next entry

### Managing Tasks
- **Active Tasks View**: Shows pending tasks with [Complete] [Delete] buttons
- **Completed Tasks View**: Shows completed tasks with timestamps and [Delete] button
- **All Tasks View**: Shows all tasks with status indicators

### Task Actions
- **Complete**: Moves task to completed state with timestamp
- **Delete**: Permanently removes task after confirmation
- **View Switch**: Instant filtering between active/completed/all tasks

## Validation Scenarios

### Form Validation
```python
# Test empty task description
assert not validate_form("")
assert not validate_form("   ")  # whitespace only

# Test valid task description
assert validate_form("Valid task description")

# Test maximum length
assert not validate_form("a" * 501)  # over 500 chars
```

### Database Integration
```python
# Test task creation flow
form_data = TaskFormData("Test task")
controller = StreamlitUIController(repository)
assert controller.create_new_task(form_data) == True

# Test task completion flow
task = repository.create_task("Test task")
assert controller.complete_task(task.id) == True

# Test task deletion flow
assert controller.delete_task(task.id) == True
```

### View Filtering
```python
# Create mixed task states
task1 = repository.create_task("Active task")
task2 = repository.create_task("To complete")
repository.mark_completed(task2.id)

# Test view filtering
active_tasks = controller.get_tasks_for_view(ViewMode.ACTIVE_TASKS)
assert len(active_tasks) == 1
assert active_tasks[0].status == "pending"

completed_tasks = controller.get_tasks_for_view(ViewMode.COMPLETED_TASKS)
assert len(completed_tasks) == 1
assert completed_tasks[0].status == "completed"
```

## Error Handling Verification

### Database Errors
- Start app with invalid database path
- Verify graceful error message display
- Ensure app doesn't crash on database errors

### Form Validation Errors
- Submit empty task description
- Verify inline error message appears
- Verify form doesn't clear error state immediately

### Network Connectivity
- No network dependency (local SQLite)
- App works completely offline

## Performance Expectations

### Response Times
- **Page Load**: < 1 second for initial load
- **Add Task**: < 100ms from click to UI update
- **Complete Task**: < 100ms from click to UI update
- **Delete Task**: < 100ms from click to UI update
- **View Switch**: < 50ms for filtering

### Resource Usage
- **Memory**: < 50MB total application memory
- **CPU**: Minimal usage during idle
- **Database**: < 10ms for CRUD operations

## Troubleshooting

### App Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.13+

# Check Streamlit installation
pip show streamlit

# Run from correct directory
pwd  # Should be project root
ls src/ui/streamlit_app.py  # Should exist
```

### Database Issues
```bash
# Check database file permissions
ls -la tasks.db

# Verify existing database layer works
python3 -c "from src.database.repository import SQLiteTaskRepository; r = SQLiteTaskRepository('tasks.db'); print('OK')"
```

### UI Not Responsive
- Refresh browser page (F5)
- Check browser console for JavaScript errors
- Restart Streamlit server (Ctrl+C, then rerun)

## Development Mode

### Live Reload
- Streamlit automatically reloads on file changes
- Save any Python file to trigger reload
- Database state persists across reloads

### Debug Mode
```bash
streamlit run src/ui/streamlit_app.py --logger.level debug
```

### Testing During Development
```bash
# Run existing tests to ensure compatibility
python3 -m pytest tests/

# Run new UI tests
python3 -m pytest tests/ui/
```

This quickstart guide ensures anyone can launch and test the Streamlit task management interface within 5 minutes.