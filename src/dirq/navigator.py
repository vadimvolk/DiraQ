"""Navigation and folder scanning functionality."""
import subprocess
from pathlib import Path
from typing import TypedDict

from dirq.config import BookmarkEntry


class NavigationEntry(TypedDict):
    """Navigation entry for display in fzf."""

    display: str
    absolute_path: Path
    source_name: str


def scan_folders(root: Path, max_depth: int) -> list[Path]:
    """
    Scan folders up to max_depth levels deep.

    Args:
        root: Root path to scan from.
        max_depth: Maximum depth to scan (0 = just root, 1 = direct subdirs, etc.).

    Returns:
        List of directory paths found.
    """
    if max_depth == 0:
        return [root]

    if not root.exists():
        return []

    results: list[Path] = []

    def _scan(current: Path, current_depth: int) -> None:
        """Recursively scan directories."""
        try:
            for entry in current.iterdir():
                if entry.is_dir():
                    results.append(entry)
                    if current_depth + 1 < max_depth:
                        _scan(entry, current_depth + 1)
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass

    _scan(root, 0)
    return results


def _has_files(path: Path) -> bool:
    """Check if a directory directly contains any files (not subdirectories)."""
    try:
        for entry in path.iterdir():
            if entry.is_file():
                return True
    except (PermissionError, OSError):
        pass
    return False


def filter_intermediate_folders(folders: list[Path]) -> list[Path]:
    """
    Filter out intermediate folders whose subdirectories are all already
    present in the list and that contain no files themselves.

    A folder like /sources/ergohaven is removed if every subdirectory of
    ergohaven/ is already in *folders* and ergohaven/ has no files.
    Leaf folders and folders with files are always kept.
    """
    folder_set = set(folders)
    result: list[Path] = []

    for folder in folders:
        try:
            subdirs = [e for e in folder.iterdir() if e.is_dir()]
        except (PermissionError, OSError):
            subdirs = []

        # Leaf folder (no subdirectories) → always keep
        if not subdirs:
            result.append(folder)
            continue

        # Keep if not every subdir is already in the list
        all_subdirs_present = all(sd in folder_set for sd in subdirs)
        if not all_subdirs_present:
            result.append(folder)
            continue

        # Keep if the folder itself contains files
        if _has_files(folder):
            result.append(folder)
            continue

        # Otherwise it's a pure pass-through → skip

    return result


def build_navigation_list(
    entries: list[BookmarkEntry],
    only: list[str] | None,
    except_names: list[str] | None,
) -> tuple[list[NavigationEntry], list[str]]:
    """
    Build navigation list from bookmark entries.

    Args:
        entries: List of bookmark entries from config.
        only: Optional list of bookmark names to include exclusively.
        except_names: Optional list of bookmark names to exclude.

    Returns:
        Tuple of (navigation entries, warning messages).

    Raises:
        ValueError: If validation fails or no valid entries found.
    """
    # Check for empty config
    if not entries:
        raise ValueError("error: no bookmarks in config. Run 'dirq save' to add bookmarks.")

    # Check mutual exclusion
    if only is not None and except_names is not None:
        raise ValueError("error: --only and --except are mutually exclusive")

    # Validate --only names exist
    if only is not None:
        entry_names = {e.name for e in entries}
        for name in only:
            if name not in entry_names:
                raise ValueError(f"error: bookmark '{name}' not found in config")

    # Filter entries
    filtered_entries = entries
    if only is not None:
        filtered_entries = [e for e in entries if e.name in only]
    elif except_names is not None:
        filtered_entries = [e for e in entries if e.name not in except_names]

    # Build navigation entries
    nav_entries: list[NavigationEntry] = []
    warnings: list[str] = []

    for entry in filtered_entries:
        # Check if folder exists
        if not entry.path.exists():
            warnings.append(
                f"warning: folder '{entry.path}' (name: {entry.name}) no longer exists, skipping"
            )
            continue

        # Scan folders
        folders = scan_folders(entry.path, entry.depth)

        # Filter out intermediate pass-through folders (depth > 0 only)
        if entry.depth > 0:
            folders = filter_intermediate_folders(folders)

        # Build display strings
        for folder in folders:
            if entry.depth == 0:
                # Depth 0: name:/full/path
                display = f"{entry.name}:{folder}"
            else:
                # Depth N: name:<relative-path>
                try:
                    relative = folder.relative_to(entry.path)
                    display = f"{entry.name}:{relative}"
                except ValueError:
                    # Fallback if relative path fails
                    display = f"{entry.name}:{folder}"

            nav_entries.append(
                NavigationEntry(
                    display=display,
                    absolute_path=folder,
                    source_name=entry.name,
                )
            )

    # Check if we have any valid entries
    if not nav_entries:
        raise ValueError("error: no valid bookmark folders found")

    return nav_entries, warnings


def run_fzf(nav_entries: list[NavigationEntry]) -> Path | None:
    """
    Run fzf with navigation entries and return selected path.

    Args:
        nav_entries: List of navigation entries to display.

    Returns:
        Selected absolute path, or None if user cancelled.

    Raises:
        FileNotFoundError: If fzf is not installed.
    """
    # Build input string for fzf
    fzf_input = "\n".join(entry["display"] for entry in nav_entries)

    try:
        result = subprocess.run(
            ["fzf"],
            input=fzf_input,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as e:
        raise FileNotFoundError("error: fzf not found. Please install fzf.") from e

    # Handle exit codes
    if result.returncode == 0:
        # User selected an item
        selected_display = result.stdout.strip()

        # Find the corresponding navigation entry
        for entry in nav_entries:
            if entry["display"] == selected_display:
                return entry["absolute_path"]

        # Fallback: shouldn't happen but handle gracefully
        return None
    elif result.returncode in (1, 130):
        # No match or Ctrl+C
        return None
    else:
        # Other error
        return None
