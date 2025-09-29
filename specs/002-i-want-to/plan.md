
# Implementation Plan: Streamlit Task Management UI

**Branch**: `002-i-want-to` | **Date**: 2025-09-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-i-want-to/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
A minimalistic Streamlit web application that provides an intuitive interface for task management, integrating with the existing SQLite database layer. Users can add new tasks, mark tasks as completed, remove tasks, and view completed task history. The UI emphasizes simplicity and distraction-free task management.

## Technical Context
**Language/Version**: Python 3.13+ (existing codebase uses 3.13.7)
**Primary Dependencies**: Streamlit (web UI framework), existing SQLite task repository
**Storage**: SQLite database (existing schema from 001-a-database-layer)
**Testing**: pytest (existing test infrastructure)
**Target Platform**: Web application via Streamlit server
**Project Type**: single (web UI component in existing Python project)
**Performance Goals**: Interactive UI response <100ms for database operations
**Constraints**: Minimalistic design, zero database schema changes, integration with existing repository layer
**Scale/Scope**: Single-user local application with simple CRUD operations

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Library-First Principle
✅ **PASS**: Streamlit UI will be implemented as a standalone module that interfaces with existing database layer through clear contracts (TaskRepository interface)

### Test-First (NON-NEGOTIABLE)
✅ **PASS**: Will follow TDD approach - write tests for UI interactions and repository integration before implementation

### Simplicity
✅ **PASS**: Streamlit provides the simplest possible web UI solution - single Python file with minimal dependencies

### Clear Purpose
✅ **PASS**: Single responsibility: "Provide web UI for task management operations"

### Interface Compliance
✅ **PASS**: Will use existing TaskRepository interface without modifications, maintaining full compatibility with database layer

**Result**: All constitutional principles satisfied. No complexity tracking required.

### Post-Design Constitution Check ✅
**Re-evaluation after Phase 1 design complete**:

- **Library-First**: ✅ UI controller and components follow clear interface contracts
- **Test-First**: ✅ Contracts define testable interfaces, quickstart provides validation scenarios
- **Simplicity**: ✅ Single Streamlit file with minimal dependencies, leverages existing repository
- **Clear Purpose**: ✅ Each component has single responsibility (controller, form, display)
- **Interface Compliance**: ✅ Extends existing TaskRepository via Protocol, no breaking changes

**Final Result**: Design maintains constitutional compliance. Ready for task generation.

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── models/              # Existing: Task model and types
├── database/            # Existing: SQLite repository implementation
├── cli/                 # Existing: CLI interface
└── ui/                  # NEW: Streamlit web interface
    └── streamlit_app.py # Main Streamlit application

tests/
├── contract/            # Existing: Repository contract tests
├── integration/         # Existing: Database integration tests
├── unit/                # Existing: Unit tests
└── ui/                  # NEW: UI integration tests
    └── test_streamlit_integration.py
```

**Structure Decision**: Single project structure extending existing codebase. New UI module will be added to src/ui/ with corresponding tests in tests/ui/. This maintains consistency with existing project organization.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Repository extension contract → test for delete_task method
- UI contracts → UI component integration tests
- Streamlit app creation → main application implementation
- Integration with existing repository → compatibility tests

**TDD Task Ordering**:
1. **Repository Extension Tests** [P] - Test delete_task method before implementation
2. **Repository Extension Implementation** - Add delete_task to SQLiteTaskRepository
3. **UI Contract Tests** [P] - Test controller and component interfaces
4. **UI Controller Implementation** - StreamlitUIController with repository integration
5. **Streamlit Components Tests** - Test individual UI components
6. **Streamlit App Implementation** - Main streamlit_app.py file
7. **Integration Tests** - End-to-end UI workflow tests
8. **Validation Tests** - Quickstart scenario verification

**Dependency Strategy**:
- Database layer extension before UI implementation
- UI contracts and controller before Streamlit components
- Component tests before component implementation
- Integration tests after all components complete

**Parallel Execution Markers**:
- [P] for independent test files (repository, UI contracts)
- [P] for non-interdependent implementation files
- Sequential for integration and validation tasks

**Estimated Output**: 15-20 numbered, ordered tasks in tasks.md focusing on:
- 4 tasks for repository extension (test + implementation + validation)
- 6 tasks for UI controller and contracts (tests + implementation)
- 4 tasks for Streamlit app components
- 3 tasks for integration and validation
- 2 tasks for quickstart verification

**Validation Approach**:
- Each task includes acceptance criteria from functional requirements
- Tasks map directly to user scenarios from specification
- Implementation tasks reference specific contract methods
- Integration tasks verify quickstart guide scenarios

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none required)

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
