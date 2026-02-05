<!--
SYNC IMPACT REPORT
==================
Version change: N/A → 1.0.0 (initial ratification)

Modified principles: N/A (initial version)

Added sections:
- Core Principles (5 principles)
- Technology Stack (Section 2)
- Development Workflow (Section 3)
- Governance

Removed sections: N/A

Templates requiring updates:
- .specify/templates/plan-template.md ✅ (compatible, no changes needed)
- .specify/templates/spec-template.md ✅ (compatible, no changes needed)
- .specify/templates/tasks-template.md ✅ (compatible, no changes needed)
- .specify/templates/checklist-template.md ✅ (compatible, no changes needed)
- .specify/templates/agent-file-template.md ✅ (compatible, no changes needed)

Follow-up TODOs: None
-->

# DIRQ Constitution

## Core Principles

### I. Simplicity

Start simple and stay simple. Complexity MUST be justified.

- YAGNI: Do not build features until they are needed
- Each module MUST have a clear, documentable purpose
- Abstractions MUST solve concrete problems, not hypothetical ones
- Configuration MUST have sensible defaults; optional overrides only when needed
- Code MUST be readable without extensive comments

**Rationale**: Simple code is easier to understand, test, maintain, and extend.

### II. Flexible Architecture

The architecture MUST be minimal yet extensible.

- Components MUST follow single responsibility principle
- Extension points MUST use composition over inheritance
- Core logic MUST be separated from I/O and CLI concerns
- Fuzzy matching and rule-based matching MUST be pluggable strategies
- New subcommands MUST be addable without modifying core logic

**Rationale**: Flexibility enables future growth without requiring architectural rewrites.

### III. Test-Driven Development (NON-NEGOTIABLE)

TDD is mandatory for all code. No exceptions.

- Tests MUST be written before implementation code
- Tests MUST fail before implementation begins (Red phase)
- Implementation MUST make tests pass with minimal code (Green phase)
- Refactoring MUST only occur with passing tests (Refactor phase)
- Code without corresponding tests MUST NOT be merged
- Test coverage MUST include unit tests for all public interfaces

**Rationale**: TDD ensures correctness, prevents regression, and drives clean design.

### IV. Minimal External Dependencies

External dependencies MUST be minimized to reduce maintenance burden and attack surface.

- Standard library solutions MUST be preferred over third-party packages
- Each external dependency MUST have explicit justification documented
- Dependencies MUST be pinned to specific versions in pyproject.toml
- Transitive dependencies MUST be audited for security and maintenance status
- UV MUST be used for all dependency management operations

**Rationale**: Fewer dependencies mean fewer breaking changes, security vulnerabilities,
and compatibility issues to track.

### V. CLI-First Design

DIRQ is a console utility. All functionality MUST be CLI-accessible.

- Single entry point command `dirq` with subcommands
- Text input via stdin/arguments, output via stdout, errors via stderr
- Exit codes MUST follow Unix conventions (0 = success, non-zero = error)
- Human-readable output by default; machine-readable (JSON) via flag
- Help text MUST be comprehensive and discoverable (`--help` on all commands)

**Rationale**: Predictable CLI behavior enables scripting, piping, and shell integration.

## Technology Stack

Mandatory technology choices for DIRQ:

- **Language**: Python 3.11+ (required minimum)
- **Package Manager**: UV (required for all dependency operations)
- **Testing**: pytest (standard Python testing)
- **Type Checking**: Type hints MUST be used; mypy or similar for validation
- **Formatting**: Consistent style enforced via ruff or similar
- **Build**: pyproject.toml for project metadata and dependencies

Third-party dependencies MUST be justified per Principle IV.

## Development Workflow

All development MUST follow this workflow:

1. **Specify**: Define what needs to be built (spec.md)
2. **Plan**: Design how to build it (plan.md)
3. **Test First**: Write failing tests for the planned work
4. **Implement**: Write minimal code to pass tests
5. **Refactor**: Improve code while keeping tests green
6. **Review**: Verify compliance with constitution before merge

### Code Review Checklist

- [ ] Tests exist and were written before implementation
- [ ] Tests fail when run against previous commit (proves TDD)
- [ ] No unnecessary external dependencies added
- [ ] CLI follows conventions (exit codes, stdout/stderr, --help)
- [ ] Type hints present on all public functions
- [ ] Code is simple and justified

## Governance

This constitution is the supreme authority for DIRQ development practices.

- All pull requests MUST comply with constitution principles
- Violations MUST be documented and resolved before merge
- Constitution amendments require:
  1. Written proposal with rationale
  2. Impact assessment on existing code
  3. Migration plan if breaking changes
  4. Version increment (MAJOR for principle removal/redefinition, MINOR for additions,
     PATCH for clarifications)

For day-to-day development guidance, refer to the generated CLAUDE.md or agent-specific
guidance files which derive from this constitution.

**Version**: 1.0.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06
