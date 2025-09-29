# Tasks: Streamlit Task Management UI

**Input**: Design documents from `/specs/002-i-want-to/`
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
- Paths assume single project structure per plan.md

## Phase 3.1: Setup

- [x] T001 Install Streamlit dependency in requirements.txt
- [x] T002 Create UI directory structure: src/ui/ and tests/ui/
- [x] T003 [P] Update .gitignore for Streamlit cache files

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- [x] T004 [P] Contract test for delete_task repository extension in tests/contract/test_repository_extension.py
- [x] T005 [P] Contract test for StreamlitUIController interface in tests/contract/test_ui_controller_contract.py
- [x] T006 [P] Integration test for task creation workflow in tests/ui/test_task_creation_integration.py
- [x] T007 [P] Integration test for task completion workflow in tests/ui/test_task_completion_integration.py
- [x] T008 [P] Integration test for task deletion workflow in tests/ui/test_task_deletion_integration.py
- [x] T009 [P] Integration test for view filtering workflow in tests/ui/test_view_filtering_integration.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

- [x] T010 Implement delete_task method in src/database/repository.py
- [x] T011 [P] Create UI data classes (ViewMode, TaskFormData, UIState) in src/ui/models.py
- [x] T012 [P] Implement StreamlitUIController in src/ui/controller.py
- [x] T013 [P] Create TaskDisplayComponent for individual task rendering in src/ui/components/task_display.py
- [x] T014 [P] Create TaskListComponent for task list rendering in src/ui/components/task_list.py
- [x] T015 [P] Create TaskFormComponent for new task creation in src/ui/components/task_form.py
- [x] T016 Implement main Streamlit application in src/ui/streamlit_app.py

## Phase 3.4: Integration

- [x] T017 Wire UI controller with repository in src/ui/streamlit_app.py
- [x] T018 Implement session state management for UI persistence
- [x] T019 Add form validation and error handling
- [x] T020 Implement view switching and filtering logic

## Phase 3.5: Polish

- [x] T021 [P] Unit tests for UI controller validation (covered by contract tests)
- [x] T022 [P] Unit tests for UI components (covered by integration tests)
- [x] T023 [P] Performance test for UI responsiveness (<100ms) in tests/integration/test_quickstart_scenarios.py
- [x] T024 [P] Validate quickstart scenarios work end-to-end
- [x] T025 Update requirements.txt with exact Streamlit version
- [x] T026 Create launch script for easy application startup

## Dependencies

- Setup (T001-T003) before everything
- Tests (T004-T009) before implementation (T010-T016)
- T010 (repository extension) blocks T012 (UI controller)
- T011-T015 (UI components) before T016 (main app)
- T016 blocks T017-T020 (integration)
- Implementation before polish (T021-T026)

## Parallel Example
```
# Launch T004-T009 together (Phase 3.2):
Task: "Contract test for delete_task repository extension in tests/contract/test_repository_extension.py"
Task: "Contract test for StreamlitUIController interface in tests/contract/test_ui_controller_contract.py"
Task: "Integration test for task creation workflow in tests/ui/test_task_creation_integration.py"
Task: "Integration test for task completion workflow in tests/ui/test_task_completion_integration.py"
Task: "Integration test for task deletion workflow in tests/ui/test_task_deletion_integration.py"
Task: "Integration test for view filtering workflow in tests/ui/test_view_filtering_integration.py"

# Launch T011-T015 together (Phase 3.3):
Task: "Create UI data classes (ViewMode, TaskFormData, UIState) in src/ui/models.py"
Task: "Implement StreamlitUIController in src/ui/controller.py"
Task: "Create TaskDisplayComponent for individual task rendering in src/ui/components/task_display.py"
Task: "Create TaskListComponent for task list rendering in src/ui/components/task_list.py"
Task: "Create TaskFormComponent for new task creation in src/ui/components/task_form.py"
```

## Notes
- [P] tasks target different files with no dependencies
- Verify all tests fail before implementing corresponding functionality
- Repository extension (delete_task) is prerequisite for UI functionality
- Streamlit app integration requires all UI components to be complete
- Follow TDD strictly: red-green-refactor cycle for each task

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - repository_extension.py → T004 (delete_task test) → T010 (implementation)
   - ui_interface.py → T005 (controller test) → T012 (controller implementation)

2. **From Data Model**:
   - UI View State → T011 (UI models)
   - Task Form Data → included in T011
   - Task entity → no changes needed (existing)

3. **From Quickstart Scenarios**:
   - Add task → T006 (creation test)
   - Mark complete → T007 (completion test)
   - Delete task → T008 (deletion test)
   - View switching → T009 (filtering test)

4. **From Technical Context**:
   - Streamlit dependency → T001
   - UI directory structure → T002
   - Performance goal (<100ms) → T023

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (T004-T005)
- [x] Repository extension has test and implementation (T004, T010)
- [x] All UI components have test coverage (T006-T009, T021-T022)
- [x] All tests come before implementation (Phase 3.2 before 3.3)
- [x] Parallel tasks truly independent (different files, no shared dependencies)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Quickstart scenarios covered by integration tests
- [x] Performance requirements addressed (T023)