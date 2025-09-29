
# Implementation Plan: Database Layer for To-Do Application

**Branch**: `001-a-database-layer` | **Date**: 2025-09-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-a-database-layer/spec.md`

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
Database layer for a to-do application enabling task creation, completion tracking, and task history retrieval using SQLite for persistent storage. Provides core data operations: create tasks, mark complete, query by status, and maintain task history with timestamps.

## Technical Context
**Language/Version**: Python 3.9+
**Primary Dependencies**: sqlite3 (built-in), pytest, dataclasses, typing
**Storage**: SQLite database (confirmed from user requirement)
**Testing**: pytest with pytest-sqlite
**Target Platform**: Cross-platform (Windows, macOS, Linux)
**Project Type**: single - determines source structure
**Performance Goals**: Sub-10ms CRUD operations, 10k tasks support, <50MB memory
**Constraints**: Local SQLite database, data persistence required, minimal external dependencies
**Scale/Scope**: Simple to-do application, small scale personal use

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution Status**: Constitution file contains template placeholders - using default best practices
- ✅ **Library-First**: Database layer implemented as standalone module with clear interface
- ✅ **Clear Purpose**: Database operations for to-do task management (contracts/task_repository.py)
- ✅ **Test-First**: Planned TDD with contract tests and integration tests
- ✅ **Simplicity**: SQLite chosen for simplicity, minimal dependencies, single table design
- ✅ **Single Responsibility**: Focus only on database layer, abstract interface separates concerns

**Post-Design Re-evaluation**:
- ✅ **No Additional Complexity**: Design maintains simple approach with single table
- ✅ **Interface Compliance**: TaskRepository abstract interface enforces contracts
- ✅ **Testability**: Clear separation allows independent testing of repository layer

**Result**: PASS - Design maintains constitutional compliance

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
├── models/
│   └── task.py           # Task entity model
├── database/
│   ├── __init__.py
│   ├── connection.py     # SQLite connection management
│   ├── migrations.py     # Database schema setup
│   └── repository.py     # Task repository operations
├── cli/
│   └── todo_cli.py       # CLI interface for testing
└── lib/
    └── __init__.py

tests/
├── contract/
│   └── test_task_repository_contract.py
├── integration/
│   └── test_database_integration.py
└── unit/
    ├── test_task_model.py
    └── test_repository.py

data/
└── todos.db              # SQLite database file
```

**Structure Decision**: Single project structure selected. Database layer implemented as standalone modules in `src/database/` with clear separation of concerns: models, database operations, and CLI interface for testing.

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
- Contract test tasks for TaskRepository interface [P]
- Model creation tasks for Task dataclass [P]
- Database setup tasks (connection, migrations) [P]
- Repository implementation tasks (SQLiteTaskRepository)
- Integration test tasks for complete user scenarios
- CLI implementation for manual testing

**Ordering Strategy**:
- TDD order: Contract tests → Models → Unit tests → Implementation → Integration tests
- Dependency order: Schema setup → Models → Repository → CLI
- Mark [P] for parallel execution (independent components)

**Specific Task Categories**:
1. **Contract Tests** (3 tasks): Repository interface, model validation, error handling
2. **Infrastructure** (4 tasks): Database schema, connections, migrations, indexes
3. **Models** (2 tasks): Task dataclass, validation logic
4. **Repository Implementation** (5 tasks): CRUD operations, query methods
5. **Integration Tests** (4 tasks): End-to-end scenarios from quickstart.md
6. **CLI Interface** (2 tasks): Basic CLI wrapper for testing

**Estimated Output**: 20 numbered, ordered tasks in tasks.md following TDD principles

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
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
