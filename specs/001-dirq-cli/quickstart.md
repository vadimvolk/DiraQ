# Quickstart: dirq CLI

**Branch**: `001-dirq-cli` | **Date**: 2026-02-06

## Prerequisites

- Python 3.11+
- [fzf](https://github.com/junegunn/fzf) installed and on PATH
- [UV](https://docs.astral.sh/uv/) for dependency management

## Project Setup

```bash
# Clone and enter project
git clone <repo-url> && cd dirq
git checkout 001-dirq-cli

# Install with UV
uv sync

# Verify installation
uv run dirq --help
```

## Development Workflow (TDD)

Per Constitution Principle III, all development follows Red-Green-Refactor:

```bash
# 1. Write a failing test
uv run pytest tests/unit/test_config.py::test_parse_valid_entry -x

# 2. Implement minimal code to pass
# ... edit src/dirq/config.py ...

# 3. Run test again (should pass)
uv run pytest tests/unit/test_config.py::test_parse_valid_entry -x

# 4. Run full suite to check for regressions
uv run pytest

# 5. Type check
uv run mypy src/dirq/
```

## Running Tests

```bash
# All tests
uv run pytest

# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# With coverage
uv run pytest --cov=dirq --cov-report=term-missing
```

## Manual Testing

```bash
# Initialize config
uv run dirq init config

# Save a bookmark
uv run dirq save ~/projects 2 proj

# Check config file
cat "${XDG_CONFIG_HOME:-~/.config}/dirq/config.rc"

# Navigate (requires fzf)
uv run dirq navigate

# Generate shell integration
uv run dirq init shell bash
# Or for fish: uv run dirq init shell fish
# Or for zsh: uv run dirq init shell zsh

# Delete a bookmark
uv run dirq delete proj
```

## Project Structure

```
src/dirq/           # Source code
├── cli.py          # Argument parsing + dispatch
├── config.py       # Config CRUD
├── navigator.py    # Folder scanning + fzf
├── shell.py        # Shell script generation
└── platform.py     # OS config paths

tests/              # Test suite
├── unit/           # Fast, isolated tests
└── integration/    # End-to-end flows
```

## Key Design Decisions

- **Zero third-party deps**: Core uses only Python stdlib (see research.md R6)
- **Tab-separated config**: Simple, handles spaces in paths (see research.md R1)
- **fzf via subprocess**: Pipe stdin, capture stdout (see research.md R3)
- **OS-specific paths**: XDG override, then platform defaults (see research.md R2)
