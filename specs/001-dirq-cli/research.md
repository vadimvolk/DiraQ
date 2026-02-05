# Research: dirq CLI - Folder Navigation Utility

**Branch**: `001-dirq-cli` | **Date**: 2026-02-06

## R1: Config File Format Design

**Decision**: Line-oriented plain text with tab-separated fields: `name\tdepth\tpath`

**Rationale**: Meets FR-014 requirement for human-readable and simple to parse. Tab separation avoids conflicts with spaces in folder names and paths. Each line represents one bookmark entry. Empty lines and lines starting with `#` are ignored (comments). The format is trivially parseable with Python's `str.split('\t')` — no external parser needed.

**Alternatives considered**:
- **INI format**: More structured but requires `configparser`. Overkill for flat list of entries. Section headers add noise.
- **JSON**: Machine-readable but not human-friendly for quick edits. Requires careful escaping. Bracket nesting for a flat list is unnecessary.
- **YAML**: Requires third-party dependency (`PyYAML`). Violates Constitution Principle IV.
- **CSV**: Comma separation conflicts with potential commas in paths (rare but possible). Tab is safer.
- **Key=value per line**: Would require multi-line entries per bookmark (name=..., depth=..., path=... with blank separator). More verbose, harder to scan visually.

**Example config.rc**:
```
# dirq bookmarks
source	2	/Users/Developer/sources
specific-folder-name	0	/Users/username/specific-folder
repos	1	/opt/repos
```

## R2: OS-Specific Config Path Resolution

**Decision**: Use `$XDG_CONFIG_HOME` if set. Otherwise fall back to OS-specific defaults using Python's `platform.system()`.

**Rationale**: XDG Base Directory Specification is the standard for Linux. macOS convention is `~/Library/Application Support`. Windows uses `%APPDATA%`. Python stdlib provides all tools needed (`os.environ`, `platform.system()`, `pathlib.Path.home()`).

| OS      | XDG_CONFIG_HOME set       | Fallback                                  |
|---------|---------------------------|-------------------------------------------|
| Linux   | `$XDG_CONFIG_HOME/dirq/`  | `~/.config/dirq/config.rc`                |
| macOS   | `$XDG_CONFIG_HOME/dirq/`  | `~/Library/Application Support/dirq/config.rc` |
| Windows | `$XDG_CONFIG_HOME/dirq/`  | `%APPDATA%\dirq\config.rc`                |

**Alternatives considered**:
- **Always use XDG**: Non-standard on macOS/Windows. Users wouldn't find config intuitively.
- **platformdirs package**: Third-party dependency. Violates Constitution Principle IV. Stdlib covers all cases.
- **Hardcode `~/.config` everywhere**: Ignores macOS/Windows conventions.

## R3: fzf Integration Pattern

**Decision**: Pipe the navigation list to fzf via `subprocess.run()` with stdin piping. Capture fzf's stdout for the selected entry. Check fzf exit code to detect Ctrl+C (exit code 130 or 1).

**Rationale**: fzf reads from stdin and writes the selection to stdout. This is the standard integration pattern. Using `subprocess.run()` with `input=` parameter and `capture_output=True` keeps it simple. No need for PTY or complex process management.

**Alternatives considered**:
- **pyfzf/iterfzf packages**: Third-party. Violates Constitution Principle IV. The subprocess approach is ~5 lines of code.
- **Write temp file, pass to fzf**: Unnecessary I/O. Piping via stdin is cleaner.
- **Build custom TUI**: Massive scope increase. fzf is a proven, fast, and feature-rich solution.

**fzf exit codes**:
- 0: Normal exit (user selected an item)
- 1: No match
- 2: Error
- 130: Interrupted (Ctrl+C)

## R4: Folder Scanning Strategy for Depth N

**Decision**: Use `pathlib.Path.iterdir()` recursively up to N levels. Only include directories (not files). Build the display string as `name:<relative-path>` where the relative path is computed from the bookmark's root path.

**Rationale**: `pathlib` is stdlib, cross-platform, and handles special characters in paths natively. Recursive scanning with a depth counter is straightforward. For depth 0, no scanning needed — just display the bookmark path itself.

**Alternatives considered**:
- **os.walk()**: Returns all levels at once, requiring depth filtering after the fact. Less efficient for shallow depths. Also doesn't respect depth limits natively.
- **glob patterns**: `Path.glob('*/')` for depth 1, `Path.glob('*/*/')` for depth 2 — but doesn't scale cleanly to depth N without string building.
- **os.scandir()**: Lower-level than `pathlib`. No advantage for this use case.

**Algorithm**:
```
def scan_folders(root: Path, max_depth: int) -> list[Path]:
    if max_depth == 0:
        return [root]
    results = []
    _scan(root, root, max_depth, 0, results)
    return results

def _scan(base, current, max_depth, current_depth, results):
    for entry in current.iterdir():
        if entry.is_dir():
            results.append(entry)
            if current_depth + 1 < max_depth:
                _scan(base, entry, max_depth, current_depth + 1, results)
```

## R5: Shell Integration Generation

**Decision**: Generate shell-specific wrapper functions and completions as string templates. Output to stdout for the user to source/eval.

**Rationale**: Each shell has different syntax for functions, completions, and variable handling. String templates with minimal interpolation keep the generation simple. Outputting to stdout lets users choose how to integrate (eval, source, redirect to file).

**Shell wrapper pattern**:
- The wrapper function calls `dirq navigate` (the binary), captures the output path, and runs `cd` on it.
- If `dirq navigate` exits non-zero (Ctrl+C, error), the wrapper does nothing.
- Completions enumerate subcommands and, for relevant subcommands, bookmark names from config.

**Alternatives considered**:
- **Write directly to shell config files**: Too invasive. Users should control their own dotfiles.
- **Provide a single POSIX shell function**: Won't work for fish (different syntax). Completions are shell-specific.

## R6: CLI Argument Parsing

**Decision**: Use `argparse` from Python stdlib with subparsers for each subcommand.

**Rationale**: `argparse` handles subcommands natively via `add_subparsers()`. It provides `--help` generation, type validation, and default values out of the box. Zero dependencies. Meets Constitution Principle V (--help on all commands).

**Alternatives considered**:
- **click**: Third-party. Violates Constitution Principle IV. Also heavier than needed.
- **typer**: Third-party. Same issue.
- **Manual sys.argv parsing**: Error-prone, no auto-generated help, reinventing the wheel.

## R7: Special Characters in Config

**Decision**: Tab-separated format naturally handles spaces and colons in names/paths. Names themselves must not contain tabs (validated on save). Unicode is handled natively by Python 3 strings and `pathlib`.

**Rationale**: The only character that would break parsing is tab (the field separator). All other characters — spaces, colons, unicode — are safe. Validation on `save` ensures names don't contain tabs. Paths on modern filesystems support full Unicode.

**Alternatives considered**:
- **Escaping scheme**: Adds complexity for an edge case (tabs in names). Simpler to just disallow tabs in names.
- **Quoted fields**: CSV-style quoting adds parser complexity. Unnecessary with tab separation.
