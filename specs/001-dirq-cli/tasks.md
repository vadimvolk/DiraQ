# Tasks: dirq CLI - Folder Navigation Utility

**Input**: Design documents from `/specs/001-dirq-cli/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-interface.md

**Tests**: Included per Constitution Principle III (TDD - NON-NEGOTIABLE). All tests follow Red-Green-Refactor.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, Python package structure, and tooling

- [ ] T001 Create project directory structure: `src/dirq/` with `__init__.py`, `__main__.py`, `cli.py`, `config.py`, `navigator.py`, `shell.py`, `platform.py`; `tests/unit/` and `tests/integration/` directories with `__init__.py` files
- [ ] T002 Initialize Python project with `uv init` and `pyproject.toml` — configure package name `dirq`, Python 3.11+ requirement, `[project.scripts]` entry point (`dirq = "dirq.cli:main"`), pytest (pinned version) as dev dependency, ruff for linting, mypy for type checking; use UV for all dependency management per Constitution Principle IV
- [ ] T003 [P] Configure ruff in `pyproject.toml` with standard Python rules and line length

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story — platform detection, config parsing, BookmarkEntry model, and CLI skeleton

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Phase

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T004 [P] Write failing tests for OS-specific config path resolution in `tests/unit/test_platform.py` — cover: XDG_CONFIG_HOME set on all platforms, XDG_CONFIG_HOME unset on macOS (~/Library/Application Support/dirq/config.rc), Linux (~/.config/dirq/config.rc), Windows (%APPDATA%\dirq\config.rc)
- [ ] T005 [P] Write failing tests for config file parsing and BookmarkEntry model in `tests/unit/test_config.py` — cover: parse valid tab-separated line into BookmarkEntry, reject lines with wrong field count, reject invalid depth (negative, >10, non-integer), reject empty name, reject name with tab character, reject non-absolute path, skip comment lines (# prefix), skip blank lines, round-trip serialize/deserialize, read full config file with multiple entries, handle corrupted file (partial parse failure = error, no partial loading), correctly parse names/paths with special characters (spaces, colons, unicode)
- [ ] T006 [P] Write failing tests for CLI argument parsing in `tests/unit/test_cli.py` — cover: top-level --help, subcommand routing for navigate/save/delete/init, save defaults (cwd for path, 0 for depth, basename for name), navigate --only and --except flags, navigate --only + --except mutual exclusion error, delete requires name-or-path argument, init config (no args), init shell requires shell-type argument

### Implementation for Foundational Phase

- [ ] T007 Implement OS-specific config path resolution in `src/dirq/platform.py` — function `get_config_path() -> Path` using `$XDG_CONFIG_HOME` if set, else OS-specific fallback per research.md R2; must pass T004 tests
- [ ] T008 Implement BookmarkEntry dataclass and config file read/write/validate in `src/dirq/config.py` — BookmarkEntry with name/depth/path fields per data-model.md, serialize as `{name}\t{depth}\t{path}`, parse with validation (name non-empty, no tabs; depth 0-10; path absolute), read_config returns list of BookmarkEntry or raises on corruption, write_config writes full entry list; must pass T005 tests
- [ ] T009 Implement CLI argument parsing and subcommand dispatch skeleton in `src/dirq/cli.py` — use argparse with subparsers per research.md R6, wire subcommands (navigate, save, delete, init with sub-subcommands config/shell), implement `main()` entry point, add `__main__.py` bootstrap (`from dirq.cli import main; main()`); must pass T006 tests. Subcommand handlers can be stubs that print "not implemented" for now.

**Checkpoint**: Foundation ready — config can be parsed, platform paths resolved, CLI routes to subcommands. User story implementation can now begin.

---

## Phase 3: User Story 3 - Initialize Configuration (Priority: P2) 🎯 MVP Prerequisite

**Goal**: First-time users can create the default config file so they can start saving bookmarks

**Independent Test**: Run `dirq init config` on a system without an existing config and verify the config file is created at the expected OS-specific location

> **Note**: Implemented before US1/US2 because saving and navigating both require a config file to exist first. This is the logical first step for any user.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US3] Write failing tests for init config in `tests/unit/test_config.py` (append to existing) — cover: create config file when none exists (creates parent dirs), inform user when config already exists (preserve existing), correct path per platform
- [ ] T011 [P] [US3] Write failing integration test for init config flow in `tests/integration/test_init_flow.py` — cover: end-to-end `dirq init config` creates file at expected location, running again reports already exists, exit codes match contract (0 for success, 0 for already exists)

### Implementation for User Story 3

- [ ] T012 [US3] Implement `init_config` command logic in `src/dirq/config.py` — create empty config file at `get_config_path()`, create parent directories if needed, check for existing file and report, output confirmation to stdout; must pass T010 tests
- [ ] T013 [US3] Wire `init config` subcommand handler in `src/dirq/cli.py` — connect argparse `init config` subcommand to `init_config` function, handle exit codes per contract (0 success, 2 filesystem error); must pass T011 tests

**Checkpoint**: Users can run `dirq init config` to create their config file. This unblocks US2 (save) and US1 (navigate).

---

## Phase 4: User Story 2 - Save a Folder Bookmark (Priority: P1)

**Goal**: Users can register a folder for quick access by running `dirq save`

**Independent Test**: Run `dirq save`, verify config file contains the new entry with correct path, depth, and name

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US2] Write failing tests for save logic in `tests/unit/test_config.py` (append to existing) — cover: save with all defaults (cwd, depth 0, basename), save with explicit path/depth/name, save with special characters in name/path (spaces, colons, unicode), save with relative path (must resolve to absolute), reject duplicate name (error message per contract), reject duplicate path (error message identifies existing entry name), reject invalid depth (0-10 range), config missing → clear error, config corrupted → clear error
- [ ] T015 [P] [US2] Write failing integration test for save flow in `tests/integration/test_save_flow.py` — cover: end-to-end save with defaults, save with explicit args, duplicate name rejection, duplicate path rejection, confirmation message format per contract, exit codes (0 success, 2 error)

### Implementation for User Story 2

- [ ] T016 [US2] Implement `save_bookmark` function in `src/dirq/config.py` — accept path (default cwd), depth (default 0), name (default basename of path), validate all fields, check for duplicate name and duplicate path in existing config, append new BookmarkEntry, write updated config; must pass T014 tests
- [ ] T017 [US2] Wire `save` subcommand handler in `src/dirq/cli.py` — connect argparse `save` subcommand to `save_bookmark` function, handle positional args with defaults per contract, output confirmation to stdout, errors to stderr, exit codes per contract; must pass T015 tests

**Checkpoint**: Users can save bookmarks. Combined with US3 (init config), users can now set up and populate their config.

---

## Phase 5: User Story 1 - Navigate to a Bookmarked Folder (Priority: P1) 🎯 Core MVP

**Goal**: Users can jump to any bookmarked folder via fzf fuzzy selection with optional --only/--except filtering

**Independent Test**: Save at least one folder, run `dirq navigate`, select from fzf, verify the selected path is output to stdout

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US1] Write failing tests for folder scanning in `tests/unit/test_navigator.py` — cover: depth 0 returns just the root path, depth 1 returns direct subdirectories, depth 2 returns subdirectories up to 2 levels deep, non-existent root path returns empty (or raises), handles symlinks and permission errors gracefully, performance with many entries
- [ ] T019 [P] [US1] Write failing tests for navigation list building and display formatting in `tests/unit/test_navigator.py` (append) — cover: depth 0 formats as `name:/full/path`, depth N formats as `name:<relative-path>`, --only filtering includes only specified names, --except filtering excludes specified names, --only + --except mutual exclusion raises error, --only with nonexistent name raises error, missing folders produce warnings and are skipped, all folders missing produces error, empty config produces helpful message, special characters in paths handled correctly
- [ ] T020 [P] [US1] Write failing tests for fzf integration in `tests/unit/test_navigator.py` (append) — cover: fzf not installed produces clear error, fzf receives correct input (piped navigation list), fzf exit code 0 returns selected path, fzf exit code 1/130 (Ctrl+C/no match) returns None, parse fzf output to extract absolute path from display format
- [ ] T021 [P] [US1] Write failing integration test for navigate flow in `tests/integration/test_navigate_flow.py` — cover: end-to-end navigate with mocked fzf (subprocess mock), navigate with --only filter, navigate with --except filter, navigate with missing folders (warnings on stderr, valid entries shown), navigate with Ctrl+C (exit code 1), navigate with no config (exit code 2), navigate with corrupted config (exit code 2), navigate with fzf not installed (exit code 2)

### Implementation for User Story 1

- [ ] T022 [US1] Implement folder scanning in `src/dirq/navigator.py` — `scan_folders(root: Path, max_depth: int) -> list[Path]` using recursive `pathlib.Path.iterdir()` per research.md R4 algorithm, handle depth 0 (return root only), depth 1-10 (recursive scan), handle non-existent paths and permission errors; must pass T018 tests
- [ ] T023 [US1] Implement navigation list building in `src/dirq/navigator.py` — `build_navigation_list(entries: list[BookmarkEntry], only: list[str] | None, except_names: list[str] | None) -> tuple[list[NavigationEntry], list[str]]` that filters entries by --only/--except, validates mutual exclusion, scans folders, formats display strings per data-model.md NavigationEntry rules, returns warnings for missing folders; must pass T019 tests
- [ ] T024 [US1] Implement fzf interaction in `src/dirq/navigator.py` — `run_fzf(entries: list[NavigationEntry]) -> Path | None` that checks fzf is on PATH, pipes display strings to fzf via `subprocess.run()` per research.md R3, parses selection to extract absolute path, handles exit codes (0=selected, 1/130=cancelled); must pass T020 tests
- [ ] T025 [US1] Wire `navigate` subcommand handler in `src/dirq/cli.py` — connect argparse `navigate` subcommand to navigator functions, orchestrate: read config → build navigation list → print warnings to stderr → run fzf → print selected path to stdout, exit codes per contract (0 success, 1 no selection, 2 error); must pass T021 tests

**Checkpoint**: Core MVP complete. Users can init config, save bookmarks, and navigate to them via fzf. This is a fully functional tool.

---

## Phase 6: User Story 4 - Initialize Shell Integration (Priority: P2)

**Goal**: Users can generate shell wrapper functions so `dirq navigate` actually changes the shell's working directory (not just prints a path)

**Independent Test**: Run `dirq init shell fish` (or bash/zsh) and verify output contains a valid shell function that wraps dirq and calls `cd`

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T026 [P] [US4] Write failing tests for shell script generation in `tests/unit/test_shell.py` — cover: fish output contains function named `dirq` wrapping `dirq navigate` with `cd`, fish output contains static completion definitions (subcommand names and flags only), bash output contains function named `dirq` with `cd`, bash output contains static completion setup, zsh output contains function named `dirq` with `cd`, zsh output contains static completion setup, unsupported shell type raises error listing supported shells
- [ ] T027 [P] [US4] Write failing integration test for init shell flow in `tests/integration/test_init_flow.py` (append to existing) — cover: end-to-end `dirq init shell fish` outputs valid fish script, `dirq init shell bash` outputs valid bash script, `dirq init shell zsh` outputs valid zsh script, `dirq init shell nush` produces error with supported shell list, exit codes per contract

### Implementation for User Story 4

- [ ] T028 [US4] Implement shell script generation in `src/dirq/shell.py` — `generate_shell_script(shell_type: str) -> str` with string templates per research.md R5 for fish, bash, zsh; each template includes wrapper function (captures `dirq navigate` output, runs `cd` if exit 0) and completion definitions; must pass T026 tests
- [ ] T029 [US4] Wire `init shell` subcommand handler in `src/dirq/cli.py` — connect argparse `init shell` subcommand to `generate_shell_script`, validate shell-type argument, print generated script to stdout, errors to stderr, exit codes per contract; must pass T027 tests

**Checkpoint**: Full shell integration available. Users can source the generated script in their shell config for seamless directory changing.

---

## Phase 7: User Story 5 - Delete a Folder Bookmark (Priority: P3)

**Goal**: Users can remove bookmarks they no longer need

**Independent Test**: Save a folder, delete it by name or path, verify it no longer appears in config or navigation list

### Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T030 [P] [US5] Write failing tests for delete logic in `tests/unit/test_config.py` (append to existing) — cover: delete by exact name match, delete by exact path match, name match takes priority over path match, no matching entry produces error, config missing → clear error, config corrupted → clear error
- [ ] T031 [P] [US5] Write failing integration test for delete flow in `tests/integration/test_save_flow.py` (append to existing or new file) — cover: end-to-end save then delete by name, save then delete by path, delete nonexistent entry, confirmation message format per contract, exit codes (0 success, 2 error)

### Implementation for User Story 5

- [ ] T032 [US5] Implement `delete_bookmark` function in `src/dirq/config.py` — accept name-or-path argument, try name match first then path match per contract, remove entry from config, write updated config; must pass T030 tests
- [ ] T033 [US5] Wire `delete` subcommand handler in `src/dirq/cli.py` — connect argparse `delete` subcommand to `delete_bookmark`, output confirmation to stdout, errors to stderr, exit codes per contract; must pass T031 tests

**Checkpoint**: All five user stories complete. Full CRUD operations + navigation + shell integration.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, robustness, and validation across all stories

- [ ] T034 [P] Add edge case tests for special characters (spaces, colons, unicode) in bookmark names and paths across `tests/unit/test_config.py` and `tests/unit/test_navigator.py`
- [ ] T035 [P] Add edge case tests for empty config (no bookmarks) navigate behavior in `tests/unit/test_navigator.py` — verify helpful message suggesting `dirq save`
- [ ] T036 Run full test suite (`uv run pytest`) and fix any failures
- [ ] T037 Run linter (`uv run ruff check src/ tests/`) and fix any issues
- [ ] T038 Run type checker (`uv run mypy src/`) and fix any type errors
- [ ] T039 Run quickstart.md validation — manually verify all commands from quickstart.md work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US3 Init Config (Phase 3)**: Depends on Foundational — needed before save/navigate
- **US2 Save (Phase 4)**: Depends on Foundational + US3 (needs config file to exist)
- **US1 Navigate (Phase 5)**: Depends on Foundational + US3 + US2 (needs saved bookmarks to navigate)
- **US4 Init Shell (Phase 6)**: Depends on Foundational only (generates scripts independently)
- **US5 Delete (Phase 7)**: Depends on Foundational + US3 (needs config operations)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US3 (Init Config, P2)**: Can start after Foundational — No dependencies on other stories. Implemented first because it's a prerequisite for save/navigate.
- **US2 (Save, P1)**: Depends on US3 (needs config file). Cannot navigate without saved bookmarks.
- **US1 (Navigate, P1)**: Depends on US2 (needs saved entries). Core value but requires save to be useful.
- **US4 (Init Shell, P2)**: Can start after Foundational — independent of US1/US2/US3. Could run in parallel with US3, US2, and US5.
- **US5 (Delete, P3)**: Can start after Foundational + US3 — independent of US1/US4. Could run in parallel with US4 and US2.

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models/parsing before services/logic
- Core implementation before CLI wiring
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: T003 can run in parallel with T001/T002
- **Phase 2**: T004, T005, T006 (all test tasks) can run in parallel; T007, T008 can run in parallel after their respective tests
- **Phase 3**: T010, T011 can run in parallel
- **Phase 4**: T014, T015 can run in parallel
- **Phase 5**: T018, T019, T020, T021 (all test tasks) can run in parallel
- **Phase 6**: T026, T027 can run in parallel; US4 can run in parallel with US3/US2 (different files)
- **Phase 7**: T030, T031 can run in parallel
- **Phase 8**: T034, T035 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Write failing tests for folder scanning in tests/unit/test_navigator.py"
Task: "Write failing tests for navigation list building in tests/unit/test_navigator.py"
Task: "Write failing tests for fzf integration in tests/unit/test_navigator.py"
Task: "Write failing integration test for navigate flow in tests/integration/test_navigate_flow.py"

# After tests written, implement sequentially:
Task: "Implement folder scanning in src/dirq/navigator.py"
Task: "Implement navigation list building in src/dirq/navigator.py" (depends on scanning)
Task: "Implement fzf interaction in src/dirq/navigator.py" (depends on list building)
Task: "Wire navigate subcommand handler in src/dirq/cli.py" (depends on all above)
```

---

## Implementation Strategy

### MVP First (Phase 1 → 2 → 3 → 4 → 5)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US3 Init Config (creates config file)
4. Complete Phase 4: US2 Save (populates config with bookmarks)
5. Complete Phase 5: US1 Navigate (core navigation via fzf)
6. **STOP and VALIDATE**: Test the full flow: init → save → navigate

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US3 Init Config → Users can create config → Validate
3. Add US2 Save → Users can save bookmarks → Validate
4. Add US1 Navigate → **Core MVP!** Users can navigate → Validate and Demo
5. Add US4 Init Shell → Full shell integration → Validate
6. Add US5 Delete → Complete CRUD → Validate
7. Polish → Production ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Tests MUST fail before implementing (TDD per Constitution Principle III)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Config file format: tab-separated `name\tdepth\tpath` per research.md R1
- All errors to stderr, output to stdout per CLI contract
- Exit codes: 0=success, 1=no selection (navigate only), 2=error
