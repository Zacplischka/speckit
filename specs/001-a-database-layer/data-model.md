# Data Model: To-Do Database Layer

## Entity Overview

### Task Entity
Represents a user-defined action item with lifecycle tracking.

**Fields**:
- `id`: Unique identifier (INTEGER PRIMARY KEY)
- `description`: Task description text (TEXT NOT NULL)
- `status`: Current task status (TEXT NOT NULL, CHECK IN ('pending', 'completed'))
- `created_at`: Task creation timestamp (DATETIME NOT NULL)
- `completed_at`: Task completion timestamp (DATETIME NULL)

**Validation Rules**:
- Description cannot be empty or null
- Status must be either 'pending' or 'completed'
- created_at is automatically set on creation
- completed_at can only be set when status is 'completed'
- completed_at must be NULL when status is 'pending'

**State Transitions**:
- New tasks start as 'pending' with completed_at = NULL
- Tasks can transition from 'pending' to 'completed'
- When transitioning to 'completed', completed_at is set to current timestamp
- Completed tasks cannot transition back to pending (immutable completion)

## Database Schema

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL CHECK(length(description) > 0),
    status TEXT NOT NULL CHECK(status IN ('pending', 'completed')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    CONSTRAINT valid_completion CHECK (
        (status = 'pending' AND completed_at IS NULL) OR
        (status = 'completed' AND completed_at IS NOT NULL)
    )
);
```

## Indexes

```sql
-- Index for filtering by status (common query pattern)
CREATE INDEX idx_tasks_status ON tasks(status);

-- Index for ordering by creation time
CREATE INDEX idx_tasks_created_at ON tasks(created_at);

-- Index for querying completed tasks by completion time
CREATE INDEX idx_tasks_completed_at ON tasks(completed_at) WHERE completed_at IS NOT NULL;
```

## Data Access Patterns

### Create Task
```sql
INSERT INTO tasks (description, status, created_at)
VALUES (?, 'pending', CURRENT_TIMESTAMP);
```

### Mark Task Complete
```sql
UPDATE tasks
SET status = 'completed', completed_at = CURRENT_TIMESTAMP
WHERE id = ? AND status = 'pending';
```

### Query All Tasks
```sql
SELECT id, description, status, created_at, completed_at
FROM tasks
ORDER BY created_at DESC;
```

### Query Pending Tasks
```sql
SELECT id, description, status, created_at, completed_at
FROM tasks
WHERE status = 'pending'
ORDER BY created_at DESC;
```

### Query Completed Tasks
```sql
SELECT id, description, status, created_at, completed_at
FROM tasks
WHERE status = 'completed'
ORDER BY completed_at DESC;
```

## Data Integrity

**Constraints**:
- Primary key ensures unique task identification
- NOT NULL constraints prevent incomplete data
- CHECK constraints enforce valid status values
- Complex constraint ensures completion timestamp consistency

**Error Handling**:
- Duplicate completion attempts return 0 affected rows
- Invalid status values rejected by CHECK constraint
- Empty descriptions rejected by CHECK constraint
- Foreign key violations not applicable (single table design)