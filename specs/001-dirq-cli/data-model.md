# Data Model: dirq CLI

**Branch**: `001-dirq-cli` | **Date**: 2026-02-06

## Entities

### BookmarkEntry

Represents a single saved folder reference in the config.

| Field | Type          | Constraints                                         |
|-------|---------------|-----------------------------------------------------|
| name  | str           | Required. Unique across all entries. No tab characters. Non-empty. |
| depth | int           | Required. Range: 0-10 inclusive. Default: 0.         |
| path  | absolute Path | Required. Unique across all entries. Stored as absolute path. |

**Validation Rules**:
- `name` must be non-empty and must not contain tab characters (`\t`)
- `name` must be unique across all entries in the config
- `path` must be an absolute path
- `path` must be unique across all entries in the config (no two entries may share the same path)
- `depth` must be an integer in range [0, 10]

**Serialization** (to config line): `{name}\t{depth}\t{path}`

### ConfigFile

Persistent storage of bookmark entries.

| Aspect    | Detail                                                       |
|-----------|--------------------------------------------------------------|
| Format    | Line-oriented plain text, tab-separated fields               |
| Location  | `$XDG_CONFIG_HOME/dirq/config.rc` or OS-specific fallback   |
| Encoding  | UTF-8                                                        |
| Comments  | Lines starting with `#` are ignored                          |
| Blanks    | Empty lines are ignored                                      |

**File format example**:
```
# dirq bookmarks
source	2	/Users/Developer/sources
specific-folder	0	/Users/username/specific-folder
repos	1	/opt/repos
```

**Validation Rules**:
- Each non-comment, non-blank line must have exactly 3 tab-separated fields
- Fields must satisfy BookmarkEntry validation rules
- A file that fails parsing is considered "corrupted" — error reported, no partial loading

### NavigationEntry

Ephemeral display item generated from BookmarkEntry + filesystem scan. Not persisted.

| Field        | Type          | Description                                   |
|--------------|---------------|-----------------------------------------------|
| display      | str           | Formatted string shown in fzf (`name:relative-path` or `name:/absolute/path`) |
| absolute_path| absolute Path | Full filesystem path for `cd` after selection |
| source_name  | str           | Bookmark name this entry was derived from (for --only/--except filtering) |

**Display format rules**:
- Depth 0: `name:/full/path/to/folder`
- Depth 1-10: `name:<relative-path-from-bookmark-root>`

## Relationships

```
ConfigFile 1──* BookmarkEntry
BookmarkEntry 1──* NavigationEntry (generated at runtime via folder scan)
```

## State Transitions

### ConfigFile Lifecycle

```
[not exists] --init config--> [empty file]
[empty file] --save--> [has entries]
[has entries] --save--> [has entries] (append)
[has entries] --delete--> [has entries] or [empty file]
[corrupted] --any command except init--> [error]
```

No in-memory state management beyond per-command execution. Each command reads the config fresh, performs its operation, and writes back if modified.
