# Feature Specification: dirq CLI - Folder Navigation Utility

**Feature Branch**: `001-dirq-cli`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Command line utility dirq for fast folder navigation using configurable bookmarks with fzf integration"

## Clarifications

### Session 2026-02-06

- Q: What syntax should navigate use for include/exclude filtering? → A: Flag syntax with `--only name1,name2` and `--except name1,name2`
- Q: Missing folder behavior during navigate - halt entirely or warn and continue? → A: Warning + continue: display warning for missing folders, then show fzf with only the valid remaining entries

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate to a Bookmarked Folder (Priority: P1)

A user wants to quickly jump to a frequently used project folder without remembering or typing the full path. They invoke `dirq navigate`, see a fuzzy-searchable list of all their bookmarked folders and subfolders, pick one, and their shell changes to that directory. Optionally, they can filter which bookmarks appear using `--only` to show specific names or `--except` to exclude specific names.

**Why this priority**: Navigation is the core value proposition of dirq. Without it, the tool has no purpose. Every other feature exists to support this one.

**Independent Test**: Can be fully tested by saving at least one folder to config, running navigate, selecting a folder from the fzf list, and verifying the shell's working directory changed to the selected folder.

**Acceptance Scenarios**:

1. **Given** a config file with at least one saved folder entry (depth 0), **When** the user runs `dirq navigate`, **Then** fzf displays the folder as `name:/full/path/to/folder` and after selection the shell changes to that folder.
2. **Given** a config entry with depth 1 for `/projects` named "proj", **When** the user runs `dirq navigate`, **Then** fzf displays each direct subfolder of `/projects` as `proj:<subfolder-name>` and after selection the shell changes to the selected subfolder's full path.
3. **Given** a config entry with depth 2 for `/projects` named "proj", **When** the user runs `dirq navigate`, **Then** fzf displays subfolders up to 2 levels deep as `proj:<relative/path>` and after selection the shell changes to the selected folder's full path.
4. **Given** the fzf selection is active, **When** the user presses Ctrl+C, **Then** no navigation occurs and no error is displayed.
5. **Given** a config entry pointing to a folder that no longer exists on the filesystem, **When** the user runs `dirq navigate`, **Then** the system displays a warning identifying the missing folder(s) and proceeds to show fzf with only the valid remaining entries.
6. **Given** all config entries point to folders that no longer exist, **When** the user runs `dirq navigate`, **Then** the system displays warnings for each missing folder and an error that no valid folders remain for navigation.
7. **Given** config entries named "proj", "work", and "docs", **When** the user runs `dirq navigate --only proj,work`, **Then** only folders from "proj" and "work" entries are shown in fzf.
8. **Given** config entries named "proj", "work", and "docs", **When** the user runs `dirq navigate --except docs`, **Then** folders from "proj" and "work" are shown, but "docs" entries are excluded.
9. **Given** the user provides both `--only` and `--except`, **When** the user runs `dirq navigate --only proj --except proj`, **Then** an error is displayed indicating the flags are mutually exclusive.
10. **Given** the user provides `--only nonexistent`, **When** the user runs `dirq navigate --only nonexistent`, **Then** an error is displayed indicating no matching bookmark names were found.
11. **Given** the config file is missing or corrupted, **When** the user runs `dirq navigate`, **Then** the system displays a clear error and does not proceed.

---

### User Story 2 - Save a Folder Bookmark (Priority: P1)

A user wants to register a folder for quick access later. They run `dirq save` with optional arguments to bookmark their current or specified directory with a name and scan depth.

**Why this priority**: Users cannot navigate without saved bookmarks. This is a prerequisite for the core feature and equally critical.

**Independent Test**: Can be fully tested by running `dirq save` and verifying the config file contains the new entry with correct path, depth, and name.

**Acceptance Scenarios**:

1. **Given** no arguments, **When** the user runs `dirq save` from `/home/user/projects`, **Then** an entry is saved with path `/home/user/projects`, depth `0`, and name `projects` (basename of current directory).
2. **Given** a specific path, depth, and name, **When** the user runs `dirq save /opt/repos 2 repos`, **Then** an entry is saved with those exact values.
3. **Given** an entry named "repos" already exists, **When** the user runs `dirq save /other/path 1 repos`, **Then** an error is displayed indicating the name is duplicated and no changes are made.
4. **Given** an entry with path `/opt/repos` already exists under the name "myrepos", **When** the user runs `dirq save /opt/repos 1 other-name`, **Then** an error is displayed indicating the path is already saved under the name "myrepos" and no changes are made.
5. **Given** the config file is missing or corrupted, **When** the user runs `dirq save`, **Then** the system displays a clear error and does not proceed.

---

### User Story 3 - Initialize Configuration (Priority: P2)

A first-time user wants to set up dirq. They run `dirq init config` to create the default configuration file so they can start saving bookmarks.

**Why this priority**: Required for first-time setup, but only done once. Returning users already have a config file.

**Independent Test**: Can be fully tested by running `dirq init config` on a system without an existing config and verifying the config file is created at the expected location.

**Acceptance Scenarios**:

1. **Given** no config file exists on macOS, **When** the user runs `dirq init config`, **Then** an empty config file is created at `$XDG_CONFIG_HOME/dirq/config.rc` (or `~/Library/Application Support/dirq/config.rc` if `$XDG_CONFIG_HOME` is unset).
2. **Given** no config file exists on Linux, **When** the user runs `dirq init config`, **Then** an empty config file is created at `$XDG_CONFIG_HOME/dirq/config.rc` (or `~/.config/dirq/config.rc` if `$XDG_CONFIG_HOME` is unset).
3. **Given** no config file exists on Windows, **When** the user runs `dirq init config`, **Then** an empty config file is created at `$XDG_CONFIG_HOME/dirq/config.rc` (or `%APPDATA%\dirq\config.rc` if `$XDG_CONFIG_HOME` is unset).
4. **Given** a config file already exists, **When** the user runs `dirq init config`, **Then** the existing config is preserved and the user is informed it already exists.
5. **Given** the parent directory does not exist, **When** the user runs `dirq init config`, **Then** the directory is created along with the config file.

---

### User Story 4 - Initialize Shell Integration (Priority: P2)

A user wants dirq to integrate with their shell so that navigation actually changes the shell's working directory (not just a subprocess) and they get tab completions. They run `dirq init shell <shell-type>` to generate the necessary shell function and completions. The generated wrapper function MUST be named `dirq` (replacing direct binary invocation). Completions are static in v1: they enumerate subcommand names and flags only (no dynamic bookmark name completion).

**Why this priority**: Shell integration is essential for the navigate command to actually change the user's working directory. Without it, dirq can only print the path, not navigate to it.

**Independent Test**: Can be fully tested by running `dirq init shell fish` (or bash/zsh) and verifying the output contains a valid shell function that wraps dirq and calls `cd` on the result.

**Acceptance Scenarios**:

1. **Given** the user's shell is fish, **When** the user runs `dirq init shell fish`, **Then** output contains a fish function definition that wraps dirq navigate and changes directory, plus completion definitions.
2. **Given** the user's shell is bash, **When** the user runs `dirq init shell bash`, **Then** output contains a bash function definition and completion setup.
3. **Given** the user's shell is zsh, **When** the user runs `dirq init shell zsh`, **Then** output contains a zsh function definition and completion setup.
4. **Given** an unsupported shell name, **When** the user runs `dirq init shell nush`, **Then** an error is displayed listing the supported shells.

---

### User Story 5 - Delete a Folder Bookmark (Priority: P3)

A user wants to remove a folder they no longer need from their bookmarks. They run `dirq delete` with either the path or name of the entry to remove.

**Why this priority**: Housekeeping feature. Not needed for core navigation flow, but important for long-term usability.

**Independent Test**: Can be fully tested by saving a folder, deleting it by name or path, and verifying it no longer appears in the config or navigation list.

**Acceptance Scenarios**:

1. **Given** an entry named "repos" exists, **When** the user runs `dirq delete repos`, **Then** the entry is removed from the config file.
2. **Given** an entry with path `/opt/repos` exists, **When** the user runs `dirq delete /opt/repos`, **Then** the entry is removed from the config file.
3. **Given** no entry matches the provided name or path, **When** the user runs `dirq delete nonexistent`, **Then** an error is displayed indicating no matching entry was found.

---

### Edge Cases

- When the config file is missing or corrupted: all subcommands (except `init config`) MUST display a clear error and halt.
- When a saved folder no longer exists on the filesystem: `navigate` MUST display a warning identifying the missing folder(s) and proceed with the remaining valid entries. If no valid entries remain, display an error.
- When the user has no entries saved and runs `navigate`: display a clear message that no bookmarks are configured and suggest using `dirq save`.
- When multiple config entries have overlapping subfolders at different depths: overlaps are ignored; duplicate paths may appear in the navigation list from different entries.
- When folder names contain special characters (spaces, colons, unicode): the system MUST handle them correctly in config storage, display, and navigation.
- When `fzf` is not installed and the user runs `navigate`: display a clear error indicating fzf is required.
- When `$XDG_CONFIG_HOME` is not set: use OS-specific defaults (macOS: `~/Library/Application Support`, Linux: `~/.config`, Windows: `%APPDATA%`).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a `navigate` subcommand that reads the config, generates a list of folders based on each entry's path and depth, presents them via fzf for selection, and outputs the selected folder's full path.
- **FR-002**: The `navigate` subcommand MUST support an `--only name1,name2` flag to include only the specified bookmark names in the navigation list.
- **FR-003**: The `navigate` subcommand MUST support an `--except name1,name2` flag to exclude the specified bookmark names from the navigation list.
- **FR-004**: The `--only` and `--except` flags MUST be mutually exclusive; using both in the same command MUST produce an error.
- **FR-005**: The system MUST provide a `save` subcommand that accepts optional path (default: current directory), depth (default: 0), and name (default: basename of path) arguments and persists them to the config file. If a relative path is provided, the system MUST resolve it to an absolute path before storage.
- **FR-006**: The system MUST reject `save` operations when the provided name already exists in the config, displaying a clear error message.
- **FR-007**: The system MUST reject `save` operations when the provided path already exists in the config under a different name, displaying an error that identifies the existing entry name.
- **FR-008**: The system MUST provide a `delete` subcommand that removes a config entry by matching either its name or path.
- **FR-009**: The system MUST provide an `init config` subcommand that creates an empty config file at the appropriate location, creating parent directories as needed.
- **FR-010**: The system MUST provide an `init shell <type>` subcommand (supporting fish, bash, zsh) that outputs a shell wrapper function enabling directory change and autocompletions.
- **FR-011**: For depth 0, the navigation list MUST display the entry as `name:/full/path/to/folder`.
- **FR-012**: For depth N (1-10), the navigation list MUST display subfolders up to N levels deep as `name:<relative/path>`.
- **FR-013**: The system MUST handle Ctrl+C during fzf selection gracefully, exiting without error.
- **FR-014**: The config file format MUST be human-readable and simple to parse, storing name, depth, and path for each entry.
- **FR-015**: When `$XDG_CONFIG_HOME` is not set, the system MUST use OS-specific defaults: macOS `~/Library/Application Support/dirq/config.rc`, Linux `~/.config/dirq/config.rc`, Windows `%APPDATA%\dirq\config.rc`.
- **FR-016**: The system MUST display a clear error when `fzf` is not installed and the user runs `navigate`.
- **FR-017**: The system MUST display a clear error and halt when the config file is missing or corrupted (for all subcommands except `init config`). A corrupted config file is one where any non-comment, non-blank line fails to parse as a valid 3-field tab-separated entry per BookmarkEntry validation rules (see data-model.md). No partial loading is permitted.
- **FR-018**: The `navigate` subcommand MUST verify that configured folder paths exist on the filesystem before building the navigation list; if any are missing, it MUST display a warning identifying the missing folder(s) and proceed with the remaining valid entries. If no valid entries remain after filtering, it MUST display an error and not proceed.
- **FR-019**: The system MUST correctly handle folder names and paths containing special characters (spaces, colons, unicode).
- **FR-020**: The depth value for a bookmark entry MUST be an integer between 0 and 10 (inclusive).

### Key Entities

- **Bookmark Entry**: Represents a saved folder reference. Attributes: name (unique identifier), path (absolute filesystem path, unique across entries), depth (integer 0-10 controlling subfolder scan depth).
- **Config File**: Persistent storage of all bookmark entries in a human-readable, line-oriented format located at the OS-appropriate config directory under `dirq/config.rc`.
- **Navigation List**: Ephemeral list of displayable folder paths generated from config entries, formatted as `name:<relative-path>` for fzf consumption. Optionally filtered by `--only` or `--except` flags.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can navigate to any bookmarked folder in under 5 seconds from command invocation to directory change.
- **SC-002**: Users can save a new folder bookmark in a single command with no more than 3 arguments.
- **SC-003**: First-time setup (init config + init shell + save first bookmark) can be completed in under 2 minutes.
- **SC-004**: The navigation list correctly reflects the folder structure on disk for all configured depth levels (0 through 10).
- **SC-005**: All subcommands provide clear, actionable error messages for invalid inputs or missing prerequisites.
- **SC-006**: Shell integration works correctly across all three supported shells (fish, bash, zsh) without manual configuration beyond sourcing the generated output.
- **SC-007**: Folder names containing special characters (spaces, colons, unicode) are correctly stored, displayed, and navigable.

## Assumptions

- `fzf` is expected to be installed separately by the user; dirq depends on it for the interactive selection interface.
- The config file uses a simple line-oriented text format (not JSON/YAML) to stay human-readable and easy to parse.
- Depth values range from 0 to 10 inclusive.
- The `navigate` subcommand itself outputs the selected path; the actual `cd` happens in the shell wrapper function generated by `init shell`.
- Paths are stored as absolute paths in the config file.
- The tool is a single-user utility; no concurrent access handling is needed for the config file.
- Both name and path are unique identifiers in the config (no two entries can share the same name or the same path).
- Overlapping subfolders from different config entries are acceptable and not deduplicated.
- No `list` subcommand is provided in v1. Users can inspect bookmarks by reading the human-readable config file directly. A `list` command may be added in a future iteration.
