# Tasks: Database Layer for To-Do Application

**Input**: Design documents from `/specs/001-a-database-layer/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `tests/` at repository root
- Using Python 3.9+ with SQLite, pytest, dataclasses, typing

## Phase 3.1: Setup
- [x] T001 Create project directory structure per implementation plan
- [x] T002 Initialize Python project with requirements.txt for pytest, dataclasses, typing dependencies
- [x] T003 [P] Create src/models/, src/database/, src/cli/, tests/contract/, tests/integration/, tests/unit/, data/ directories
- [x] T004 [P] Create __init__.py files in all src/ subdirectories

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [x] T005 [P] Contract test for TaskRepository.create_task() in tests/contract/test_task_repository_contract.py
- [x] T006 [P] Contract test for TaskRepository.mark_completed() in tests/contract/test_task_repository_contract.py
- [x] T007 [P] Contract test for TaskRepository query methods in tests/contract/test_task_repository_contract.py
- [x] T008 [P] Integration test for basic task lifecycle scenario in tests/integration/test_database_integration.py
- [x] T009 [P] Integration test for edge cases scenario in tests/integration/test_database_integration.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [x] T010 [P] Task dataclass model in src/models/task.py with validation
- [x] T011 [P] Database connection management in src/database/connection.py
- [x] T012 [P] Database schema migration in src/database/migrations.py
- [x] T013 SQLiteTaskRepository implementation - create_task() method in src/database/repository.py
- [x] T014 SQLiteTaskRepository implementation - mark_completed() method in src/database/repository.py
- [x] T015 SQLiteTaskRepository implementation - query methods in src/database/repository.py
- [x] T016 [P] CLI interface for testing in src/cli/todo_cli.py

## Phase 3.4: Integration
- [x] T017 Database schema initialization with indexes in src/database/migrations.py
- [x] T018 Error handling and validation in SQLiteTaskRepository
- [x] T019 Connection pooling and cleanup in src/database/connection.py

## Phase 3.5: Polish
- [x] T020 [P] Unit tests for Task model validation in tests/unit/test_task_model.py
- [x] T021 [P] Unit tests for SQLiteTaskRepository methods in tests/unit/test_repository.py
- [x] T022 Performance verification for sub-10ms operations
- [x] T023 [P] Documentation and type hints verification
- [x] T024 Run quickstart.md manual testing scenarios

## Dependencies
- Setup (T001-T004) before everything
- Contract tests (T005-T009) before implementation (T010-T016)
- T010 blocks T013-T015 (repository needs Task model)
- T011-T012 block T013-T015 (repository needs database infrastructure)
- T016 needs T010 and T013-T015 (CLI needs working repository)
- Core implementation before integration (T017-T019)
- Everything before polish (T020-T024)

## Parallel Example
```bash
# Phase 3.2: Launch contract tests together
Task: "Contract test for TaskRepository.create_task() in tests/contract/test_task_repository_contract.py"
Task: "Contract test for TaskRepository.mark_completed() in tests/contract/test_task_repository_contract.py"
Task: "Contract test for TaskRepository query methods in tests/contract/test_task_repository_contract.py"
Task: "Integration test for basic task lifecycle scenario in tests/integration/test_database_integration.py"
Task: "Integration test for edge cases scenario in tests/integration/test_database_integration.py"

# Phase 3.3: Launch models in parallel
Task: "Task dataclass model in src/models/task.py with validation"
Task: "Database connection management in src/database/connection.py"
Task: "Database schema migration in src/database/migrations.py"
```

## Detailed Task Specifications

### T005: Contract test for TaskRepository.create_task()
**File**: `tests/contract/test_task_repository_contract.py`
**Purpose**: Test that create_task() follows the interface contract
**Must Test**:
- Returns Task with assigned ID
- Sets status to 'pending'
- Sets created_at timestamp
- Validates non-empty description
- Raises ValueError for empty description

### T006: Contract test for TaskRepository.mark_completed()
**File**: `tests/contract/test_task_repository_contract.py`
**Purpose**: Test that mark_completed() follows the interface contract
**Must Test**:
- Returns True when marking pending task complete
- Returns False when task already completed
- Returns False when task ID not found
- Sets completed_at timestamp when completing

### T007: Contract test for TaskRepository query methods
**File**: `tests/contract/test_task_repository_contract.py`
**Purpose**: Test all query methods follow interface contracts
**Must Test**:
- get_all_tasks() returns all tasks ordered by created_at DESC
- get_pending_tasks() returns only pending tasks
- get_completed_tasks() returns only completed tasks ordered by completed_at DESC
- get_task_by_id() returns correct task or None

### T008: Integration test for basic task lifecycle
**File**: `tests/integration/test_database_integration.py`
**Purpose**: Test complete user scenario from quickstart.md
**Must Test**:
- Complete Scenario 1: Basic Task Lifecycle from quickstart.md
- Database persistence across operations
- Proper timestamps and status transitions

### T009: Integration test for edge cases
**File**: `tests/integration/test_database_integration.py`
**Purpose**: Test edge cases from quickstart.md
**Must Test**:
- Double completion attempts
- Invalid task IDs
- Empty descriptions
- Database constraints enforcement

### T010: Task dataclass model
**File**: `src/models/task.py`
**Purpose**: Implement Task dataclass per contracts/task_repository.py
**Must Include**:
- All fields from contract: id, description, status, created_at, completed_at
- TaskStatus Literal type
- Validation for description non-empty
- Proper typing with Optional and datetime

### T013-T015: SQLiteTaskRepository implementation
**File**: `src/database/repository.py`
**Purpose**: Implement all TaskRepository abstract methods
**Must Include**:
- All 6 abstract methods from contract
- SQL queries from data-model.md
- Error handling per contract specifications
- Database transaction management

## Notes
- [P] tasks = different files, no dependencies between them
- All tests MUST FAIL before implementing features (TDD requirement)
- Follow exact SQL patterns from data-model.md
- Use dataclasses and typing as specified in research.md
- Commit after each completed task
- Validate against quickstart.md scenarios throughout

## Task Generation Rules Applied

1. **From Contracts**:
   ✅ TaskRepository contract → 3 contract test tasks [P] (T005-T007)
   ✅ Each abstract method → implementation task (T013-T015)

2. **From Data Model**:
   ✅ Task entity → model creation task [P] (T010)
   ✅ Database schema → migration task [P] (T012)
   ✅ Indexes → integration task (T017)

3. **From Quickstart Scenarios**:
   ✅ Scenario 1 → integration test [P] (T008)
   ✅ Scenario 2 → integration test [P] (T009)
   ✅ CLI usage → CLI implementation (T016)

4. **Ordering Applied**:
   ✅ Setup → Tests → Models → Services → Integration → Polish
   ✅ TDD: All tests before implementation
   ✅ Dependencies respected in task sequence

## Validation Checklist
*GATE: Checked before execution*

- [x] All contracts have corresponding tests (T005-T007 cover TaskRepository)
- [x] All entities have model tasks (T010 covers Task entity)
- [x] All tests come before implementation (T005-T009 before T010-T016)
- [x] Parallel tasks truly independent (different files marked [P])
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Quickstart scenarios covered in integration tests
- [x] All functional requirements from spec.md addressed