"""Config file reading, writing, and validation."""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BookmarkEntry:
    """A single folder bookmark."""

    name: str
    depth: int
    path: Path

    def __post_init__(self) -> None:
        """Validate bookmark entry fields."""
        if not self.name:
            raise ValueError("Name must not be empty")
        if "\t" in self.name:
            raise ValueError("Name must not contain tab characters")
        if not isinstance(self.path, Path):
            self.path = Path(self.path)
        if not self.path.is_absolute():
            raise ValueError("Path must be absolute")
        if not (0 <= self.depth <= 10):
            raise ValueError("Depth must be between 0 and 10")


def parse_line(line: str) -> BookmarkEntry | None:
    """
    Parse a single config line into a BookmarkEntry.

    Args:
        line: A tab-separated string with format: name\\tdepth\\tpath

    Returns:
        BookmarkEntry if valid, None if comment or blank line.

    Raises:
        ValueError: If line is malformed or validation fails.
    """
    # Only strip trailing whitespace, preserve tabs for field detection
    line = line.rstrip()

    # Skip comments and blank lines
    if not line or line.startswith("#"):
        return None

    # Split and validate field count
    parts = line.split("\t")
    if len(parts) != 3:
        raise ValueError(f"Expected 3 fields, got {len(parts)}")

    name, depth_str, path_str = parts

    # Parse depth as integer
    try:
        depth = int(depth_str)
    except ValueError as e:
        raise ValueError(f"invalid literal for int() with base 10: '{depth_str}'") from e

    # Create and validate BookmarkEntry
    return BookmarkEntry(name=name, depth=depth, path=Path(path_str))


def serialize_entry(entry: BookmarkEntry) -> str:
    """
    Serialize a BookmarkEntry to a config line.

    Args:
        entry: BookmarkEntry to serialize.

    Returns:
        Tab-separated string: name\\tdepth\\tpath
    """
    return f"{entry.name}\t{entry.depth}\t{entry.path}"


def read_comment_header(config_path: Path) -> str:
    """
    Read leading comment and blank lines from a config file.

    Args:
        config_path: Path to the config file.

    Returns:
        String containing all leading comment/blank lines, including newlines.
        Returns empty string if file doesn't exist.
    """
    if not config_path.exists():
        return ""
    header_lines: list[str] = []
    with config_path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.rstrip()
            if not stripped or stripped.startswith("#"):
                header_lines.append(line)
            else:
                break
    return "".join(header_lines)


def read_config(config_path: Path) -> list[BookmarkEntry]:
    """
    Read and parse a config file.

    Args:
        config_path: Path to the config file.

    Returns:
        List of BookmarkEntry objects.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If config file is corrupted (parse failure).
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    entries = []
    with config_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            try:
                entry = parse_line(line)
                if entry is not None:
                    entries.append(entry)
            except ValueError as e:
                raise ValueError(f"Failed to parse line {line_num}: {e}") from e

    return entries


def write_config(
    config_path: Path, entries: list[BookmarkEntry], header: str = ""
) -> None:
    """
    Write entries to a config file.

    Args:
        config_path: Path to the config file.
        entries: List of BookmarkEntry objects to write.
        header: Comment header to write before entries.
    """
    # Create parent directories if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with config_path.open("w", encoding="utf-8") as f:
        if header:
            f.write(header)
        for entry in entries:
            f.write(serialize_entry(entry) + "\n")


def init_config(config_path: Path) -> str:
    """
    Initialize a new config file.

    Creates an empty config file at the specified path if it doesn't exist.
    If the file already exists, leaves it unchanged and returns an info message.

    Args:
        config_path: Path to the config file.

    Returns:
        Success or informational message.

    Raises:
        OSError: If filesystem permission issues prevent file creation.
    """
    if config_path.exists():
        return f"Config already exists at {config_path}"

    # Create parent directories if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Create config file with format comment
    config_path.write_text(
        "# dirq bookmarks: name<TAB>depth<TAB>/absolute/path\n"
        "# depth 0 = folder itself, 1-10 = scan subfolders to that level\n"
        "# this file is regenerated when adding or removing folders\n"
    )

    return f"Created config at {config_path}"


def save_bookmark(
    config_path: Path,
    path: Path | None = None,
    depth: int = 0,
    name: str | None = None,
) -> str:
    """
    Save a folder bookmark to the config file.

    Args:
        config_path: Path to the config file.
        path: Path to bookmark (default: current working directory).
        depth: Subfolder scan depth 0-10 (default: 0).
        name: Unique bookmark name (default: basename of path).

    Returns:
        Success confirmation message.

    Raises:
        ValueError: If validation fails or duplicates detected.
    """
    # Auto-create config if missing
    if not config_path.exists():
        init_config(config_path)

    # Read existing config and comment header
    header = read_comment_header(config_path)
    entries = read_config(config_path)

    # Apply defaults
    if path is None:
        path = Path.cwd()
    else:
        path = Path(path)

    # Resolve to absolute path
    if not path.is_absolute():
        path = path.resolve()

    if name is None:
        name = path.name

    # Validate that path exists on disk
    if not path.exists():
        raise ValueError(f"error: path '{path}' does not exist")
    if not path.is_dir():
        raise ValueError(f"error: path '{path}' is not a directory")

    # Create new entry (this validates depth, name, path)
    new_entry = BookmarkEntry(name=name, depth=depth, path=path)

    # Check for duplicate name
    for entry in entries:
        if entry.name == name:
            raise ValueError(f"error: name '{name}' already exists in config")

    # Check for duplicate path
    for entry in entries:
        if entry.path == path:
            raise ValueError(f"error: path '{path}' already saved under name '{entry.name}'")

    # Append new entry and write config
    entries.append(new_entry)
    write_config(config_path, entries, header=header)

    return f"Saved '{name}' -> {path} (depth: {depth})"


def delete_bookmark(config_path: Path, name_or_path: str) -> str:
    """
    Delete a bookmark from the config file.

    Matching logic: First try exact match against bookmark names.
    If no name matches, try exact match against paths.

    Args:
        config_path: Path to the config file.
        name_or_path: Bookmark name or absolute path to delete.

    Returns:
        Success confirmation message.

    Raises:
        FileNotFoundError: If config file doesn't exist.
        ValueError: If no matching bookmark found or config corrupted.
    """
    # Read existing config and comment header
    header = read_comment_header(config_path)
    entries = read_config(config_path)

    # Try to find by name first
    deleted_name = None
    for i, entry in enumerate(entries):
        if entry.name == name_or_path:
            deleted_name = entry.name
            entries.pop(i)
            break

    # If not found by name, try by path
    if deleted_name is None:
        path_to_match = Path(name_or_path)
        for i, entry in enumerate(entries):
            if entry.path == path_to_match:
                deleted_name = entry.name
                entries.pop(i)
                break

    # If still not found, raise error
    if deleted_name is None:
        raise ValueError(f"error: no bookmark found matching '{name_or_path}'")

    # Write updated config
    write_config(config_path, entries, header=header)

    return f"Deleted '{deleted_name}'"
