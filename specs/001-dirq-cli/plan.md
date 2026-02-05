# Implementation Plan: dirq CLI - Folder Navigation Utility

**Branch**: `001-dirq-cli` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-dirq-cli/spec.md`

## Summary

Build `dirq`, a Python CLI utility for fast folder navigation using configurable bookmarks with fzf integration. The tool provides subcommands to save/delete folder bookmarks in a line-oriented config file, generate shell integration scripts (fish/bash/zsh), and navigate via fzf-powered fuzzy selection. Core logic is separated from CLI and I/O concerns, following a composition-based architecture that allows pluggable subcommands.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: None beyond stdlib for core logic; fzf as external runtime dependency (not a Python package)
**Storage**: Plain text config file at OS-appropriate config directory (`dirq/config.rc`)
**Testing**: pytest
**Package Manager**: UV (required per Constitution Principle IV)
**Type Checking**: mypy (required per Constitution Technology Stack)
**Target Platform**: macOS, Linux, Windows (cross-platform)
**Project Type**: Single CLI application
**Performance Goals**: Navigation list generation in under 2 seconds for up to 1000 entries at depth 10
**Constraints**: Zero Python third-party dependencies for core functionality; fzf must be available on PATH
**Scale/Scope**: Single-user utility, config files with up to hundreds of bookmark entries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity | PASS | Single-purpose CLI tool. No unnecessary abstractions. Line-oriented config format. Sensible defaults for all optional args. |
| II. Flexible Architecture | PASS | Core logic separated from CLI/I/O. Subcommands addable without modifying core. Config parsing, folder scanning, and display formatting are independent modules. |
| III. TDD (NON-NEGOTIABLE) | PASS | All code will follow Red-Green-Refactor. Tests written before implementation. pytest used throughout. |
| IV. Minimal Dependencies | PASS | Zero Python third-party dependencies. stdlib only (pathlib, os, sys, subprocess, platform). fzf is external runtime tool, not a Python package. |
| V. CLI-First Design | PASS | Single `dirq` entry point with subcommands. stdout for output, stderr for errors. Exit codes follow Unix conventions. --help on all commands. JSON output flag (`--json`) deferred for v1: primary outputs are single path strings (already machine-parseable) or shell scripts; structured JSON wrapping adds no value for a single-user navigation tool. |

**Gate result**: ALL PASS (pre-design). Post-Phase 1 re-check: ALL PASS. Design artifacts (research.md, data-model.md, contracts/, quickstart.md) confirm zero third-party deps, clean module separation, TDD workflow, and Unix CLI conventions.

## Project Structure

### Documentation (this feature)

```text
specs/001-dirq-cli/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli-interface.md # CLI contract (subcommands, args, exit codes)
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── dirq/
│   ├── __init__.py
│   ├── __main__.py          # Entry point: python -m dirq
│   ├── cli.py               # Argument parsing, subcommand dispatch
│   ├── config.py            # Config file reading/writing/validation
│   ├── navigator.py         # Folder scanning, list building, fzf interaction
│   ├── shell.py             # Shell integration script generation
│   └── platform.py          # OS-specific config path resolution

tests/
├── unit/
│   ├── test_config.py       # Config parsing, validation, CRUD
│   ├── test_navigator.py    # Folder scanning, list formatting, filtering
│   ├── test_shell.py        # Shell script generation
│   ├── test_platform.py     # OS-specific path resolution
│   └── test_cli.py          # Argument parsing, subcommand routing
└── integration/
    ├── test_save_flow.py    # End-to-end save scenarios
    ├── test_navigate_flow.py # End-to-end navigate scenarios (mocked fzf)
    └── test_init_flow.py    # End-to-end init scenarios
```

**Structure Decision**: Single project layout. All source under `src/dirq/` as a Python package. Tests mirror source structure with unit and integration separation. No web/mobile components.

## Complexity Tracking

No violations to justify. Architecture is minimal and aligns with all constitution principles.
