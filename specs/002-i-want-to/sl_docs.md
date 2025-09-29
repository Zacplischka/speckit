# Streamlit Documentation Reference

## Table of Contents
1. [Installation & Setup](#installation--setup)
2. [Core Concepts](#core-concepts)
3. [SQLite Integration](#sqlite-integration)
4. [Key API Components](#key-api-components)
5. [CRUD Operations](#crud-operations)
6. [Best Practices](#best-practices)
7. [Example Implementation](#example-implementation)

## Installation & Setup

### Basic Installation
```bash
pip install streamlit
```

### Running a Streamlit App
```bash
streamlit run app.py
```

### Additional Dependencies for SQLite
```bash
pip install sqlalchemy  # Required for st.connection with SQL
```

## Core Concepts

### 1. App Execution Model
- **Script Rerun**: Entire Python script reruns from top to bottom when:
  - Source code is modified
  - User interacts with widgets
  - `st.rerun()` is called explicitly
- **Development Flow**: Save file → Streamlit auto-detects changes → App refreshes
- **Fast Interactive Loop**: Edit → Save → See results immediately

### 2. Data Flow Architecture
- Unique top-to-bottom execution model
- Callbacks run before the rest of the script
- Use `@st.cache_data` decorator to optimize performance and avoid re-running expensive computations

### 3. Widget State Management
- Widgets are treated like variables
- When a widget value changes, the script reruns
- Access widget values through unique keys or variable assignment
- Example: `user_input = st.text_input("Enter text", key="unique_key")`

### 4. Session State
```python
# Initialize session state
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# Update state
st.session_state.counter += 1
```

## SQLite Integration

### Connection Setup

#### Method 1: Using secrets.toml
Create `.streamlit/secrets.toml`:
```toml
[connections.mydb]
url = "sqlite:///path/to/database.db"
```

In your app:
```python
import streamlit as st

conn = st.connection('mydb', type='sql')
```

#### Method 2: Direct Connection
```python
import streamlit as st

# For local SQLite file
conn = st.connection('sql', url="sqlite:///mydatabase.db")

# For in-memory database
conn = st.connection('sql', url="sqlite:///:memory:")
```

### Querying Data
```python
# Simple query with caching
df = conn.query("SELECT * FROM tasks", ttl=600)  # Cache for 10 minutes

# Query without caching
df = conn.query("SELECT * FROM tasks", ttl=0)

# Parameterized query for security
df = conn.query(
    "SELECT * FROM tasks WHERE status = :status",
    params={"status": "pending"}
)
```

### Complex Database Operations
```python
# Access SQLAlchemy session for complex operations
with conn.session as session:
    # Perform inserts, updates, deletes
    session.execute(
        "INSERT INTO tasks (description, status) VALUES (:desc, :status)",
        {"desc": "New task", "status": "pending"}
    )
    session.commit()
```

## Key API Components

### Display Elements

#### st.write()
Universal display function that handles multiple data types:
```python
st.write("Text")
st.write(dataframe)
st.write({"dict": "data"})
```

#### st.dataframe()
Interactive data display:
```python
st.dataframe(df, use_container_width=True)
```

#### st.table()
Static table display:
```python
st.table(df)
```

#### st.metric()
Display metrics with optional delta:
```python
st.metric("Total Tasks", 42, delta=5)
```

### Input Widgets

#### Text Input
```python
task_description = st.text_input("Task Description")
long_text = st.text_area("Details", height=150)
```

#### Buttons
```python
if st.button("Create Task"):
    # Handle task creation
    pass

# Button with key for state management
if st.button("Complete", key=f"complete_{task_id}"):
    # Mark task as complete
    pass
```

#### Selection Widgets
```python
status = st.selectbox("Status", ["pending", "completed"])
selected = st.multiselect("Select Tasks", options=task_list)
choice = st.radio("Filter", ["All", "Pending", "Completed"])
```

#### Checkbox
```python
show_completed = st.checkbox("Show completed tasks")
```

### Layout Components

#### Columns
```python
col1, col2, col3 = st.columns(3)
with col1:
    st.write("Column 1")
with col2:
    st.write("Column 2")
with col3:
    st.write("Column 3")
```

#### Sidebar
```python
with st.sidebar:
    st.header("Filters")
    status_filter = st.selectbox("Status", ["All", "Pending", "Completed"])
```

#### Container
```python
with st.container():
    st.write("This is inside a container")
```

#### Expander
```python
with st.expander("Show Details"):
    st.write("Detailed information here")
```

#### Tabs
```python
tab1, tab2 = st.tabs(["Active Tasks", "Completed Tasks"])
with tab1:
    st.write("Active tasks content")
with tab2:
    st.write("Completed tasks content")
```

### Forms
```python
with st.form("task_form"):
    description = st.text_input("Task Description")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])
    submitted = st.form_submit_button("Create Task")

    if submitted:
        # Process form data
        pass
```

## CRUD Operations

### st.data_editor for Interactive CRUD
```python
# Enable row addition/deletion
edited_df = st.data_editor(
    df,
    num_rows="dynamic",  # Allow adding/deleting rows
    column_config={
        "description": st.column_config.TextColumn(
            "Task Description",
            help="Enter task description",
            required=True,
        ),
        "status": st.column_config.SelectboxColumn(
            "Status",
            options=["pending", "completed"],
            required=True,
        ),
        "created_at": st.column_config.DatetimeColumn(
            "Created",
            format="DD/MM/YYYY HH:mm",
            disabled=True,  # Make read-only
        ),
    },
    hide_index=True,
    use_container_width=True,
)

# Detect changes
if edited_df is not None:
    # Compare with original df to find changes
    # Update database accordingly
    pass
```

### Handling Data Editor Changes
```python
# Track edited rows
edited_rows = st.session_state.get("edited_rows", {})

# Use on_change callback
def handle_edit():
    # Process changes
    pass

edited_df = st.data_editor(
    df,
    key="data_editor",
    on_change=handle_edit,
)
```

## Best Practices

### 1. Performance Optimization
```python
# Cache expensive operations
@st.cache_data
def load_data():
    return pd.read_sql("SELECT * FROM large_table", conn)

# Cache database connections
@st.cache_resource
def get_database_connection():
    return sqlite3.connect('database.db')
```

### 2. Error Handling
```python
try:
    result = conn.query("SELECT * FROM tasks")
    st.success("Data loaded successfully")
except Exception as e:
    st.error(f"Database error: {e}")
```

### 3. User Feedback
```python
# Progress indicators
with st.spinner("Loading data..."):
    data = load_data()

# Success/Error messages
st.success("Task created successfully!")
st.error("Failed to create task")
st.warning("Please fill all required fields")
st.info("Tip: Use filters to find tasks quickly")
```

### 4. State Management Best Practices
```python
# Initialize all session state variables at the top
def init_session_state():
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []
    if 'filter' not in st.session_state:
        st.session_state.filter = 'all'

init_session_state()
```

### 5. Rerun Control
```python
# Force a rerun after state change
st.session_state.task_added = True
st.rerun()

# Prevent unnecessary reruns
if st.session_state.get('processed', False):
    return
```

## Example Implementation

### Complete Task Manager Example
```python
import streamlit as st
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Task Manager",
    page_icon="✅",
    layout="wide"
)

# Initialize connection
conn = st.connection('tasks_db', type='sql')

# Header
st.title("📝 Task Manager")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    status_filter = st.radio(
        "Show tasks:",
        ["All", "Pending", "Completed"]
    )

# Create task form
with st.form("new_task", clear_on_submit=True):
    col1, col2 = st.columns([3, 1])
    with col1:
        new_task = st.text_input("Task description")
    with col2:
        submit = st.form_submit_button("Add Task", use_container_width=True)

    if submit and new_task:
        with conn.session as session:
            session.execute(
                "INSERT INTO tasks (description, status, created_at) VALUES (:desc, 'pending', :created)",
                {"desc": new_task, "created": datetime.now()}
            )
            session.commit()
        st.success("Task added successfully!")
        st.rerun()

# Load and display tasks
query = "SELECT * FROM tasks"
if status_filter != "All":
    query += f" WHERE status = '{status_filter.lower()}'"
query += " ORDER BY created_at DESC"

df_tasks = conn.query(query, ttl=0)

if not df_tasks.empty:
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tasks", len(df_tasks))
    with col2:
        pending = len(df_tasks[df_tasks['status'] == 'pending'])
        st.metric("Pending", pending)
    with col3:
        completed = len(df_tasks[df_tasks['status'] == 'completed'])
        st.metric("Completed", completed)

    # Display tasks
    st.subheader("Tasks")

    # Make tasks editable
    edited_df = st.data_editor(
        df_tasks,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "description": st.column_config.TextColumn("Description"),
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["pending", "completed"],
            ),
            "created_at": st.column_config.DatetimeColumn(
                "Created",
                disabled=True,
                format="DD/MM/YYYY HH:mm"
            ),
            "completed_at": st.column_config.DatetimeColumn(
                "Completed",
                disabled=True,
                format="DD/MM/YYYY HH:mm"
            )
        },
        hide_index=True,
        use_container_width=True,
        disabled=["id", "created_at", "completed_at"]
    )

    # Save changes button
    if st.button("Save Changes", type="primary"):
        # Update database with changes
        # Implementation depends on change detection logic
        st.success("Changes saved!")
        st.rerun()
else:
    st.info("No tasks found. Create your first task above!")

# Footer
st.divider()
st.caption("Task Manager v1.0 - Built with Streamlit")
```

### Connection Configuration (.streamlit/secrets.toml)
```toml
[connections.tasks_db]
url = "sqlite:///tasks.db"
```

### Requirements.txt
```
streamlit>=1.28.0
sqlalchemy>=2.0.0
pandas>=2.0.0
```

## Additional Resources

### 2025 Updates
- **st.pdf**: Render PDF documents directly in apps
- **Cell selections**: Support for dataframe cell selection
- **Sparklines**: Add sparklines to st.metric
- **Editable ListColumn**: Make list columns editable in data_editor
- **Directory upload**: Support for uploading entire directories

### Useful Links
- Official Documentation: https://docs.streamlit.io
- API Reference: https://docs.streamlit.io/develop/api-reference
- Community Forum: https://discuss.streamlit.io
- GitHub: https://github.com/streamlit/streamlit

### Common Patterns

#### Auto-refresh
```python
import time

# Auto-refresh every 5 seconds
while True:
    # Your app logic here
    time.sleep(5)
    st.rerun()
```

#### File Upload
```python
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)
```

#### Download Button
```python
csv = df.to_csv(index=False)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="tasks.csv",
    mime="text/csv"
)
```

#### Progress Bar
```python
import time

progress_bar = st.progress(0)
for i in range(100):
    progress_bar.progress(i + 1)
    time.sleep(0.01)
```

This documentation provides a comprehensive reference for building a Streamlit application with SQLite integration for your task management system.