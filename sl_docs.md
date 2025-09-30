# Streamlit Documentation for Todo App Implementation

## Overview
This document contains relevant Streamlit documentation for implementing a todo list application over the existing SQLite database layer.

---

## Core Widgets for Todo App

### Text Input Widgets
1. **st.text_input**
   - Display a single-line text input widget
   - Useful for entering new todo items

2. **st.text_area**
   - Display a multi-line text input widget
   - Good for longer todo descriptions

### Interaction Widgets
1. **st.button**
   - Display a button widget
   - Can trigger actions like adding or completing todos
   - Supports `on_click` callbacks for cleaner state management

2. **st.checkbox**
   - Display a checkbox widget
   - Perfect for marking todos as complete/incomplete
   - Supports `on_change` callbacks

### Form Handling
1. **st.form**
   - Groups related input widgets together
   - Helps organize todo input and submission
   - Batches elements together with a Submit button

2. **st.form_submit_button**
   - Display a form submit button
   - Finalizes todo creation or updates

### Data Display Widgets
1. **st.dataframe**
   - Display a dataframe as an interactive table
   - Excellent for displaying todo lists
   - Allows interactive data manipulation

2. **st.data_editor**
   - Display a data editor widget
   - Enables dynamic editing of todo lists

---

## Session State Management

### Fundamentals
- Session state is a way to share variables between reruns, for each user session
- Each browser tab creates a new session
- Streamlit reruns scripts from top to bottom on each interaction, normally resetting variables
- Session state persists across app reruns

### Basic Usage Pattern
```python
# Initialize if not exists
if 'key' not in st.session_state:
    st.session_state.key = 'value'

# Read value
st.write(st.session_state.key)

# Update value
st.session_state.key = 'new_value'
```

### Access Methods
- Dictionary-style: `st.session_state['key']`
- Attribute-style: `st.session_state.key`

### Important Limitations
- Session state exists only while browser tab is open
- Does not persist if Streamlit server crashes
- Cannot set state for `st.button` and `st.file_uploader`

### Advanced Features
- Supports callbacks with `on_click` and `on_change`
- Can pass arguments to callbacks
- Integrates with widget states

### Serialization Option
- Can enforce pickle-serializable objects with `runner.enforceSerializableSessionState`

---

## Database Connections

### SQLite Connection Setup

#### Installation
```bash
pip install SQLAlchemy==1.4.0
```

#### Secrets Configuration
Create `.streamlit/secrets.toml`:
```toml
[connections.pets_db]
url = "sqlite:///pets.db"
```

#### Basic Connection Code
```python
conn = st.connection('pets_db', type='sql')
with conn.session as s:
    s.execute('CREATE TABLE IF NOT EXISTS pet_owners (person TEXT, pet TEXT);')
    s.execute('INSERT INTO pet_owners VALUES ("Jerry", "Fish");')
    s.commit()
```

#### Querying Data
```python
# Simple read-only queries with caching
pets = conn.query('SELECT * FROM pet_owners')
st.dataframe(pets)
```

### Connection Features
- **st.connection()**: Easily connect apps to data and APIs with just a few lines of code
- **SQLConnection**: All SQLConnections in Streamlit use SQLAlchemy
- **Query method**: `.query()` convenience method for simple, read-only queries with caching and error handling
- **Session property**: `.session` property for complex database interactions using regular SQLAlchemy Session

### Best Practices
- Use existing Python drivers
- Provide intuitive read methods
- Support configuration through secrets and environment variables
- Handle connection staleness and thread safety
- Use global secrets management

---

## Caching Mechanisms

### st.cache_data
- Recommended for caching data computations
- Creates a copy of returned data
- Ideal for:
  - Loading DataFrames
  - Transforming data
  - API calls
  - Running ML model inference
- Prevents mutation and concurrency issues by copying data

**Example for database query caching:**
```python
@st.cache_data
def query_database():
    return pd.read_sql_query("SELECT * from table", connection)
```

### st.cache_resource
- Used for caching global resources
- Does not create a copy of the returned object
- Best for:
  - Database connections
  - Machine learning models
  - Unserializable objects

### Key Differences
- `st.cache_data` serializes and copies data
- `st.cache_resource` stores the original object reference

### Cache Control
Can control cache size/duration with:
- `ttl`: Time to live
- `max_entries`: Maximum cache entries

### General Guidance
- Use `st.cache_data` by default
- Be cautious with `st.cache_resource` to avoid mutation issues

---

## Execution Flow Control

### st.rerun()

#### Function Signature
```python
st.rerun(*, scope="app")
```

#### Description
- Immediately stops the current script execution and queues the script to run again
- Supports two scope options:
  - `"app"` (default): Full app rerun
  - `"fragment"`: Rerun specific fragment

#### Usage Considerations
- Additional script runs may be inefficient and slower
- Can potentially cause infinite looping if misused
- Best used sparingly during prototyping
- Excessive reruns may complicate app logic and be harder to follow

#### Alternatives (Recommended)

**1. Callbacks:**
```python
# Instead of st.rerun()
if st.button("Foo"):
    st.session_state.value = "Foo"
    st.rerun()

# Use callback (cleaner)
def update_value():
    st.session_state.value = "Bar"
st.button("Bar", on_click=update_value)
```

**2. Containers:**
Can help manage app state and updates without explicit reruns

#### Caution
While powerful, st.rerun() should be used judiciously to maintain app performance and clarity

---

## Implementation Recommendations for Todo App

### Architecture Pattern
1. **Database Layer**: Use existing SQLiteTaskRepository
2. **Connection Management**: Use `st.cache_resource` for database connection
3. **Data Queries**: Use `st.cache_data` for query results (with TTL if needed)
4. **State Management**: Use session state for temporary UI state
5. **Updates**: Use callbacks on buttons/forms instead of st.rerun()

### Example Structure
```python
import streamlit as st
from src.database.repository import SQLiteTaskRepository

@st.cache_resource
def get_repository():
    return SQLiteTaskRepository("data/todos.db")

def add_task_callback():
    if st.session_state.new_task_input:
        repo = get_repository()
        repo.create_task(st.session_state.new_task_input)
        st.session_state.new_task_input = ""

def mark_complete_callback(task_id):
    repo = get_repository()
    repo.mark_completed(task_id)

# UI
st.title("Todo List")

# Input form
st.text_input("New task", key="new_task_input")
st.button("Add", on_click=add_task_callback)

# Display tasks
repo = get_repository()
tasks = repo.get_pending_tasks()
for task in tasks:
    col1, col2 = st.columns([4, 1])
    with col1:
        st.write(task.description)
    with col2:
        st.button("Complete", key=f"complete_{task.id}",
                 on_click=mark_complete_callback, args=(task.id,))
```

### Key Considerations
1. Avoid calling database operations directly in the main script flow
2. Use callbacks to trigger database changes
3. Cache the repository connection with `st.cache_resource`
4. Consider caching query results if performance becomes an issue
5. Use session state only for temporary UI state, not for database data
6. Let Streamlit's natural rerun behavior handle UI updates after callbacks