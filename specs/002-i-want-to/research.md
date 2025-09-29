# Research: Streamlit Task Management UI

## Streamlit Framework Research

### Decision: Streamlit for Web UI
**Rationale**: Streamlit is the simplest Python framework for creating web applications with minimal boilerplate. Perfect fit for minimalistic UI requirements.

**Key Benefits**:
- Single Python file application
- Automatic reactivity for state management
- Built-in widgets for forms and interactions
- No HTML/CSS/JavaScript knowledge required
- Excellent for data applications and simple UIs

**Alternatives Considered**:
- Flask/FastAPI: Too complex for simple UI, requires HTML templates
- Django: Massive overkill for single-page task management
- Tkinter: Desktop-only, doesn't meet web requirement

### Streamlit Best Practices for Task Management

**State Management Pattern**:
- Use `st.session_state` for persistent data across interactions
- Initialize state on first load
- Update state through callbacks

**UI Layout Pattern**:
- `st.sidebar` for navigation between views
- `st.columns` for horizontal layout of actions
- `st.container` for grouping related elements

**Form Handling Pattern**:
- `st.form` with `submit_button` for adding new tasks
- Individual buttons for task actions (complete, delete)
- Input validation before database operations

## Task Deletion Implementation Research

### Decision: Add delete_task method to existing repository
**Rationale**: The current repository only supports create and mark_completed. Need delete functionality for "remove tasks" requirement.

**Implementation Approach**:
```python
def delete_task(self, task_id: int) -> bool:
    """Delete a task permanently from the database."""
    # DELETE FROM tasks WHERE id = ?
    # Return True if task was deleted, False if not found
```

**Database Considerations**:
- SQLite DELETE statement with WHERE clause
- Handle foreign key constraints (none in current schema)
- Return boolean to indicate success/failure
- Use same error handling pattern as existing methods

**Alternatives Considered**:
- Soft delete (status = 'deleted'): Adds complexity, not in requirements
- Archive pattern: Overkill for simple task management

## Streamlit-Repository Integration Pattern

### Decision: Repository instance in session state
**Rationale**: Streamlit apps are stateless by default. Repository needs to persist across page refreshes and user interactions.

**Pattern**:
```python
if 'repository' not in st.session_state:
    st.session_state.repository = SQLiteTaskRepository("tasks.db")

# Use throughout app as: st.session_state.repository.method()
```

**Database Connection Management**:
- Use persistent file-based database (not :memory:)
- Repository handles connection lifecycle automatically
- Context manager ensures proper cleanup

### UI Refresh Strategy
**Decision**: Automatic refresh after each operation
**Rationale**: Streamlit's reactive model automatically re-runs script after user interactions, showing updated data immediately.

**Implementation**:
- No manual refresh needed
- State changes trigger automatic UI updates
- Repository queries always fetch fresh data

## Testing Strategy for Streamlit Apps

### Decision: Integration testing with simulated user interactions
**Rationale**: Streamlit apps are UI-heavy, best tested through user interaction simulation.

**Testing Approach**:
- Use temporary in-memory database for isolation
- Mock Streamlit components for unit tests
- Integration tests verify repository interaction
- Manual testing for UI/UX validation

**Test Structure**:
```python
def test_add_task_integration():
    # Setup in-memory repository
    # Simulate form submission
    # Verify task created in database
    # Verify UI shows new task
```

## Performance Considerations

### Decision: Keep UI simple for <100ms response
**Rationale**: SQLite operations are fast enough for single-user application. UI simplicity ensures responsive interactions.

**Optimization Strategy**:
- Minimal database queries per page load
- Simple list rendering (no pagination needed)
- Direct repository calls (no caching layer)

**Monitoring**:
- Use Streamlit's built-in performance metrics
- Monitor database query times during testing

## Configuration and Deployment

### Decision: Simple file-based configuration
**Rationale**: Single-user application doesn't need complex configuration system.

**Configuration**:
- Database path as constant in application
- Default to "tasks.db" in current directory
- Environment variable override for testing

**Deployment**:
- `streamlit run src/ui/streamlit_app.py`
- No additional server configuration needed
- Works locally without internet connection