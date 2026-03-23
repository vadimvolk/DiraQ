**English** | **[Русский](README.ru.md)**

# dirq

![CI](https://github.com/vadimvolk/DiraQ/actions/workflows/ci.yml/badge.svg)

Fast folder navigation CLI with fuzzy-finding powered by [fzf](https://github.com/junegunn/fzf). Bookmark directories with configurable scan depths and jump to them instantly.

## Prerequisites

- Python 3.11+
- [fzf](https://github.com/junegunn/fzf) installed and on PATH
- [uv](https://docs.astral.sh/uv/) (recommended for installation)

## Installation

### As a uv script (recommended)

Install globally as a tool with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install git+https://github.com/vadimvolk/DiraQ.git
```

Or from a local clone:

```bash
git clone https://github.com/vadimvolk/DiraQ.git && cd dirq
uv tool install .
```

This makes `dirq` available everywhere without activating a virtual environment.

### For development

```bash
git clone https://github.com/vadimvolk/DiraQ.git && cd dirq
uv sync
```

Then run via `uv run dirq` or activate the virtual environment.

### With pip

```bash
pip install -e .
```

## Quick Start

```bash
# Create the config file
dirq init config

# Set up shell integration (fish, bash, or zsh)
dirq init shell bash
# Follow the printed instructions to source the wrapper

# Save a bookmark (current directory, depth 0)
dirq save

# Save with a custom name and subfolder depth
dirq save ~/projects 2 proj

# Navigate bookmarks via fzf
dirq navigate
```

## Usage

### Save bookmarks

```bash
dirq save [path] [depth] [name]
```

All arguments are optional. Defaults: `path` = current directory, `depth` = 0, `name` = directory basename. Depth (0-10) controls how many levels of subdirectories are scanned.

### Navigate

```bash
dirq navigate              # Browse all bookmarks
dirq navigate --only a,b   # Include only named bookmarks
dirq navigate --except c   # Exclude named bookmarks
```

Selecting a folder in fzf changes your working directory (via the shell wrapper).

### Delete bookmarks

```bash
dirq delete proj           # By name
dirq delete ~/projects     # By path
```

### List bookmarks

```bash
dirq list
```

### Shell integration

```bash
dirq init shell fish
dirq init shell bash
dirq init shell zsh
```

Generates a wrapper function and completions for your shell.

## Configuration

Config file location (auto-detected):

| OS | Path |
|---|---|
| Linux | `~/.config/dirq/config.rc` |
| macOS | `~/Library/Application Support/dirq/config.rc` |
| Windows | `%APPDATA%\dirq\config.rc` |

Respects `$XDG_CONFIG_HOME` when set.

Format (tab-separated):

```
proj	2	/home/user/projects
docs	0	/home/user/Documents
```

## Development

```bash
uv run pytest              # Run all tests
uv run ruff check .        # Lint
uv run mypy src/dirq/      # Type check
```

## Design

- **Zero Python dependencies** -- stdlib only for all core logic
- **fzf as the sole external dependency** -- fuzzy finding via subprocess
- **OS-native config paths** -- XDG on Linux, native on macOS/Windows
- **Shell wrappers** -- enables actual `cd` (not just path output)

## License

See [LICENSE](LICENSE) for details.
