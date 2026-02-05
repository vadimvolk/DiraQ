# CLI Interface Contract: dirq

**Branch**: `001-dirq-cli` | **Date**: 2026-02-06

## Entry Point

```
dirq <subcommand> [options] [arguments]
```

Binary name: `dirq`
Python module: `python -m dirq`

## Subcommands

### `dirq navigate`

Navigate to a bookmarked folder via fzf selection.

```
dirq navigate [--only name1,name2] [--except name1,name2]
```

| Argument    | Type   | Required | Description                                      |
|-------------|--------|----------|--------------------------------------------------|
| `--only`    | string | No       | Comma-separated list of bookmark names to include |
| `--except`  | string | No       | Comma-separated list of bookmark names to exclude |

**Constraints**: `--only` and `--except` are mutually exclusive.

**Output** (stdout): The absolute path of the selected folder (single line, no trailing newline decoration).

**Exit codes**:

| Code | Meaning                                    |
|------|--------------------------------------------|
| 0    | Success: path printed to stdout            |
| 1    | No selection made (Ctrl+C or fzf no match) |
| 2    | Error: config missing/corrupted, fzf not installed, no valid entries, or invalid flags |

**Stderr output**:
- Warnings for missing folders (e.g., `warning: folder '/old/path' (name: proj) no longer exists, skipping`)
- Errors for fatal conditions (e.g., `error: config file not found. Run 'dirq init config' first.`)

---

### `dirq save`

Save a folder bookmark to config.

```
dirq save [path] [depth] [name]
```

| Argument | Type   | Required | Default                    | Description                 |
|----------|--------|----------|----------------------------|-----------------------------|
| `path`   | string | No       | Current working directory  | Absolute path to bookmark   |
| `depth`  | int    | No       | 0                          | Subfolder scan depth (0-10) |
| `name`   | string | No       | Basename of path           | Unique bookmark identifier  |

**Output** (stdout): Confirmation message (e.g., `Saved 'repos' -> /opt/repos (depth: 2)`)

**Exit codes**:

| Code | Meaning                                                  |
|------|----------------------------------------------------------|
| 0    | Success: entry saved                                     |
| 2    | Error: duplicate name, duplicate path, invalid depth, config missing/corrupted |

**Stderr output**:
- `error: name 'repos' already exists in config`
- `error: path '/opt/repos' already saved under name 'myrepos'`
- `error: depth must be an integer between 0 and 10`

---

### `dirq delete`

Remove a bookmark from config.

```
dirq delete <name-or-path>
```

| Argument       | Type   | Required | Description                         |
|----------------|--------|----------|-------------------------------------|
| `name-or-path` | string | Yes      | Bookmark name or absolute path      |

**Matching logic**: First try exact match against bookmark names. If no name matches, try exact match against paths.

**Output** (stdout): Confirmation message (e.g., `Deleted 'repos'`)

**Exit codes**:

| Code | Meaning                                            |
|------|----------------------------------------------------|
| 0    | Success: entry removed                             |
| 2    | Error: no matching entry, config missing/corrupted |

**Stderr output**:
- `error: no bookmark found matching 'nonexistent'`

---

### `dirq init config`

Create the default config file.

```
dirq init config
```

No arguments.

**Output** (stdout): Confirmation message (e.g., `Created config at /home/user/.config/dirq/config.rc`)

**Exit codes**:

| Code | Meaning                                          |
|------|--------------------------------------------------|
| 0    | Success: config created, or already exists       |
| 2    | Error: filesystem permission issue               |

**Stderr output**:
- `Config already exists at /home/user/.config/dirq/config.rc` (exit 0, informational)

---

### `dirq init shell`

Generate shell integration script.

```
dirq init shell <shell-type>
```

| Argument     | Type   | Required | Description                      |
|--------------|--------|----------|----------------------------------|
| `shell-type` | string | Yes      | One of: `fish`, `bash`, `zsh`    |

**Output** (stdout): Shell function definition + completion setup, ready to be sourced/eval'd.

**Exit codes**:

| Code | Meaning                          |
|------|----------------------------------|
| 0    | Success: script printed          |
| 2    | Error: unsupported shell type    |

**Stderr output**:
- `error: unsupported shell 'nush'. Supported: fish, bash, zsh`

## Global Behavior

- All errors go to stderr, never stdout
- All subcommands support `--help`
- `dirq --help` shows top-level help with subcommand list
- Exit code 0 = success, 1 = no selection (navigate-specific), 2 = error
- No color output by default (shell-friendly)
