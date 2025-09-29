# Quickstart: To-Do Database Layer

## Setup and Basic Usage

### 1. Initialize Database
```python
from src.database.connection import get_connection
from src.database.migrations import create_schema
from src.database.repository import SQLiteTaskRepository

# Initialize database with schema
connection = get_connection("data/todos.db")
create_schema(connection)

# Create repository instance
repo = SQLiteTaskRepository("data/todos.db")
```

### 2. Create Tasks
```python
# Create a new task
task1 = repo.create_task("Buy groceries")
print(f"Created task {task1.id}: {task1.description}")

# Create another task
task2 = repo.create_task("Walk the dog")
print(f"Created task {task2.id}: {task2.description}")
```

### 3. View Tasks
```python
# Get all tasks
all_tasks = repo.get_all_tasks()
print(f"Total tasks: {len(all_tasks)}")

# Get only pending tasks
pending = repo.get_pending_tasks()
print(f"Pending tasks: {len(pending)}")
for task in pending:
    print(f"  {task.id}: {task.description}")
```

### 4. Complete Tasks
```python
# Mark first task as completed
success = repo.mark_completed(task1.id)
if success:
    print(f"Task {task1.id} marked as completed")

# Verify completion
completed = repo.get_completed_tasks()
print(f"Completed tasks: {len(completed)}")
for task in completed:
    print(f"  {task.id}: {task.description} (completed: {task.completed_at})")
```

### 5. Query Specific Task
```python
# Get task by ID
task = repo.get_task_by_id(task1.id)
if task:
    print(f"Task {task.id}: {task.description} [{task.status}]")
```

## Expected Output
```
Created task 1: Buy groceries
Created task 2: Walk the dog
Total tasks: 2
Pending tasks: 2
  1: Buy groceries
  2: Walk the dog
Task 1 marked as completed
Completed tasks: 1
  1: Buy groceries (completed: 2025-09-29 10:30:45)
Task 1: Buy groceries [completed]
```

## Test Scenarios

### Scenario 1: Basic Task Lifecycle
```python
# Given: Empty database
assert len(repo.get_all_tasks()) == 0

# When: Create a task
task = repo.create_task("Test task")

# Then: Task exists and is pending
assert task.id is not None
assert task.status == 'pending'
assert task.completed_at is None
assert len(repo.get_pending_tasks()) == 1

# When: Mark task complete
success = repo.mark_completed(task.id)

# Then: Task is completed
assert success == True
completed_task = repo.get_task_by_id(task.id)
assert completed_task.status == 'completed'
assert completed_task.completed_at is not None
assert len(repo.get_completed_tasks()) == 1
assert len(repo.get_pending_tasks()) == 0
```

### Scenario 2: Edge Cases
```python
# Test double completion
task = repo.create_task("Double completion test")
repo.mark_completed(task.id)
second_completion = repo.mark_completed(task.id)  # Should return False

# Test invalid task ID
invalid_completion = repo.mark_completed(99999)  # Should return False

# Test empty description (should raise ValueError)
try:
    repo.create_task("")
    assert False, "Should have raised ValueError"
except ValueError:
    pass  # Expected
```

## File Structure After Quickstart
```
data/
└── todos.db              # SQLite database with tasks table

src/
├── models/
│   └── task.py           # Task model implementation
├── database/
│   ├── connection.py     # Database connection management
│   ├── migrations.py     # Schema creation
│   └── repository.py     # Task repository implementation
└── cli/
    └── todo_cli.py       # CLI for manual testing
```