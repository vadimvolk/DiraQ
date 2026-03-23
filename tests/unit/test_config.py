"""Tests for config file parsing and BookmarkEntry model."""
import tempfile
from pathlib import Path

import pytest

from dirq.config import (
    BookmarkEntry,
    parse_line,
    read_comment_header,
    read_config,
    serialize_entry,
    write_config,
)


class TestBookmarkEntry:
    """Test BookmarkEntry dataclass validation and serialization."""

    def test_parse_valid_line(self) -> None:
        """Parse a valid tab-separated line into BookmarkEntry."""
        line = "source\t2\t/Users/Developer/sources"
        entry = parse_line(line)
        assert entry.name == "source"
        assert entry.depth == 2
        assert entry.path == Path("/Users/Developer/sources")

    def test_reject_wrong_field_count_too_few(self) -> None:
        """Reject lines with too few fields."""
        line = "source\t2"
        with pytest.raises(ValueError, match="Expected 3 fields"):
            parse_line(line)

    def test_reject_wrong_field_count_too_many(self) -> None:
        """Reject lines with too many fields."""
        line = "source\t2\t/path\textra"
        with pytest.raises(ValueError, match="Expected 3 fields"):
            parse_line(line)

    def test_reject_invalid_depth_negative(self) -> None:
        """Reject negative depth."""
        line = "source\t-1\t/path"
        with pytest.raises(ValueError, match="Depth must be"):
            parse_line(line)

    def test_reject_invalid_depth_above_10(self) -> None:
        """Reject depth > 10."""
        line = "source\t11\t/path"
        with pytest.raises(ValueError, match="Depth must be"):
            parse_line(line)

    def test_reject_invalid_depth_non_integer(self) -> None:
        """Reject non-integer depth."""
        line = "source\tabc\t/path"
        with pytest.raises(ValueError, match="invalid literal"):
            parse_line(line)

    def test_reject_empty_name(self) -> None:
        """Reject empty name."""
        line = "\t2\t/path"
        with pytest.raises(ValueError, match="Name must not be empty"):
            parse_line(line)

    def test_reject_name_with_tab(self) -> None:
        """Reject name containing tab character."""
        line = "my\tname\t2\t/path"
        with pytest.raises(ValueError, match="Expected 3 fields"):
            parse_line(line)

    def test_reject_non_absolute_path(self) -> None:
        """Reject relative path."""
        line = "source\t2\trelative/path"
        with pytest.raises(ValueError, match="Path must be absolute"):
            parse_line(line)

    def test_skip_comment_lines(self) -> None:
        """Skip lines starting with #."""
        line = "# this is a comment"
        entry = parse_line(line)
        assert entry is None

    def test_skip_blank_lines(self) -> None:
        """Skip empty lines."""
        line = ""
        entry = parse_line(line)
        assert entry is None

    def test_skip_whitespace_only_lines(self) -> None:
        """Skip lines with only whitespace."""
        line = "   \t  "
        entry = parse_line(line)
        assert entry is None

    def test_serialize_round_trip(self) -> None:
        """Serialize and deserialize should be idempotent."""
        original = BookmarkEntry(name="repos", depth=1, path=Path("/opt/repos"))
        serialized = serialize_entry(original)
        parsed = parse_line(serialized)
        assert parsed == original

    def test_special_characters_in_name_spaces(self) -> None:
        """Parse names with spaces."""
        line = "my source\t2\t/path"
        entry = parse_line(line)
        assert entry.name == "my source"

    def test_special_characters_in_name_colon(self) -> None:
        """Parse names with colons."""
        line = "proj:main\t2\t/path"
        entry = parse_line(line)
        assert entry.name == "proj:main"

    def test_special_characters_in_path_spaces(self) -> None:
        """Parse paths with spaces."""
        line = "source\t2\t/Users/My Documents"
        entry = parse_line(line)
        assert entry.path == Path("/Users/My Documents")

    def test_special_characters_in_path_unicode(self) -> None:
        """Parse paths with unicode characters."""
        line = "source\t2\t/Users/文档"
        entry = parse_line(line)
        assert entry.path == Path("/Users/文档")


class TestReadConfig:
    """Test reading full config files."""

    def test_read_multiple_entries(self) -> None:
        """Read a config file with multiple entries."""
        content = """# dirq bookmarks
source\t2\t/Users/Developer/sources
specific-folder\t0\t/Users/username/specific-folder
repos\t1\t/opt/repos
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rc") as f:
            f.write(content)
            f.flush()
            config_path = Path(f.name)

        try:
            entries = read_config(config_path)
            assert len(entries) == 3
            assert entries[0].name == "source"
            assert entries[1].name == "specific-folder"
            assert entries[2].name == "repos"
        finally:
            config_path.unlink()

    def test_read_empty_config(self) -> None:
        """Read an empty config file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rc") as f:
            f.write("")
            f.flush()
            config_path = Path(f.name)

        try:
            entries = read_config(config_path)
            assert entries == []
        finally:
            config_path.unlink()

    def test_read_config_only_comments(self) -> None:
        """Read a config with only comments and blank lines."""
        content = """# Just comments
# No actual entries

"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rc") as f:
            f.write(content)
            f.flush()
            config_path = Path(f.name)

        try:
            entries = read_config(config_path)
            assert entries == []
        finally:
            config_path.unlink()

    def test_corrupted_config_raises_error(self) -> None:
        """Reject corrupted config (partial parse failure)."""
        content = """source\t2\t/valid/path
corrupted line
repos\t1\t/another/valid"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rc") as f:
            f.write(content)
            f.flush()
            config_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Failed to parse"):
                read_config(config_path)
        finally:
            config_path.unlink()

    def test_missing_config_file_raises(self) -> None:
        """Raise FileNotFoundError for missing config."""
        config_path = Path("/nonexistent/config.rc")
        with pytest.raises(FileNotFoundError):
            read_config(config_path)


class TestReadCommentHeader:
    """Test reading comment headers from config files."""

    def test_read_comment_header(self) -> None:
        """Read leading comment lines from a config file."""
        content = "# line one\n# line two\nsource\t2\t/sources\n"
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rc") as f:
            f.write(content)
            f.flush()
            config_path = Path(f.name)

        try:
            header = read_comment_header(config_path)
            assert header == "# line one\n# line two\n"
        finally:
            config_path.unlink()

    def test_read_comment_header_with_blank_lines(self) -> None:
        """Read leading comments and blank lines."""
        content = "# comment\n\n# another\nsource\t2\t/sources\n"
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rc") as f:
            f.write(content)
            f.flush()
            config_path = Path(f.name)

        try:
            header = read_comment_header(config_path)
            assert header == "# comment\n\n# another\n"
        finally:
            config_path.unlink()

    def test_read_comment_header_no_comments(self) -> None:
        """Return empty string when no leading comments."""
        content = "source\t2\t/sources\n"
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rc") as f:
            f.write(content)
            f.flush()
            config_path = Path(f.name)

        try:
            header = read_comment_header(config_path)
            assert header == ""
        finally:
            config_path.unlink()

    def test_read_comment_header_only_comments(self) -> None:
        """Return all lines when file is only comments."""
        content = "# just comments\n# nothing else\n"
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rc") as f:
            f.write(content)
            f.flush()
            config_path = Path(f.name)

        try:
            header = read_comment_header(config_path)
            assert header == "# just comments\n# nothing else\n"
        finally:
            config_path.unlink()


class TestWriteConfig:
    """Test writing config files."""

    def test_write_config_creates_file(self) -> None:
        """Write entries to a new config file."""
        entries = [
            BookmarkEntry(name="source", depth=2, path=Path("/sources")),
            BookmarkEntry(name="repos", depth=1, path=Path("/repos")),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            write_config(config_path, entries)

            content = config_path.read_text()
            assert "source\t2\t/sources" in content
            assert "repos\t1\t/repos" in content

    def test_write_config_overwrites_existing(self) -> None:
        """Overwrite existing config file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rc") as f:
            f.write("old\t0\t/old/path\n")
            f.flush()
            config_path = Path(f.name)

        try:
            entries = [BookmarkEntry(name="new", depth=1, path=Path("/new/path"))]
            write_config(config_path, entries)

            content = config_path.read_text()
            assert "new\t1\t/new/path" in content
            assert "old" not in content
        finally:
            config_path.unlink()

    def test_write_empty_list(self) -> None:
        """Write an empty entry list (clears config)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            write_config(config_path, [])

            content = config_path.read_text()
            assert content.strip() == ""

    def test_write_config_with_header(self) -> None:
        """Write entries with a comment header."""
        entries = [BookmarkEntry(name="source", depth=2, path=Path("/sources"))]
        header = "# my header\n# line two\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            write_config(config_path, entries, header=header)

            content = config_path.read_text()
            assert content.startswith("# my header\n# line two\n")
            assert "source\t2\t/sources" in content


class TestInitConfig:
    """Test init config functionality."""

    def test_create_config_when_none_exists(self) -> None:
        """Create config file when none exists, including parent directories."""
        from dirq.config import init_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nested" / "dirs" / "config.rc"
            result = init_config(config_path)

            assert config_path.exists()
            assert result == f"Created config at {config_path}"

            content = config_path.read_text()
            assert "this file is regenerated when adding or removing folders" in content

    def test_inform_when_config_already_exists(self) -> None:
        """Inform user when config already exists (preserve existing)."""
        from dirq.config import init_config

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            # Create existing config with content
            config_path.write_text("existing\t0\t/existing\n")

            result = init_config(config_path)

            # Should preserve existing content
            content = config_path.read_text()
            assert "existing\t0\t/existing" in content
            assert result == f"Config already exists at {config_path}"

    def test_correct_path_per_platform(self) -> None:
        """Verify init_config uses platform-specific path."""
        from dirq.platform import get_config_path

        # This test verifies integration with platform.get_config_path
        # We don't create the actual file in the real location
        config_path = get_config_path()
        assert "dirq" in str(config_path)
        assert "config.rc" in str(config_path)


class TestSaveBookmark:
    """Test save bookmark functionality."""

    def test_save_with_all_defaults(self) -> None:
        """Save with all defaults (cwd, depth 0, basename)."""
        import os

        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            config_path.touch()
            tmpdir_resolved = Path(tmpdir).resolve()

            # Change to tmpdir and save
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = save_bookmark(config_path)

                entries = read_config(config_path)
                assert len(entries) == 1
                assert entries[0].name == tmpdir_resolved.name
                assert entries[0].depth == 0
                assert entries[0].path == tmpdir_resolved
                assert f"Saved '{tmpdir_resolved.name}'" in result
            finally:
                os.chdir(original_cwd)

    def test_save_with_explicit_args(self) -> None:
        """Save with explicit path, depth, and name."""
        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            config_path.touch()

            save_dir = Path(tmpdir) / "myproject"
            save_dir.mkdir()

            result = save_bookmark(config_path, path=save_dir, depth=2, name="proj")

            entries = read_config(config_path)
            assert len(entries) == 1
            assert entries[0].name == "proj"
            assert entries[0].depth == 2
            assert entries[0].path == save_dir
            assert "Saved 'proj' -> " in result
            assert "(depth: 2)" in result

    def test_save_with_special_characters_in_name(self) -> None:
        """Save with special characters in name (spaces, colons)."""
        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            config_path.touch()

            save_dir = Path(tmpdir) / "test"
            save_dir.mkdir()

            # Name with spaces
            save_bookmark(config_path, path=save_dir, name="my project")
            entries = read_config(config_path)
            assert entries[0].name == "my project"

            # Name with colon
            write_config(config_path, [])
            save_bookmark(config_path, path=save_dir, name="proj:main")
            entries = read_config(config_path)
            assert entries[0].name == "proj:main"

    def test_save_with_special_characters_in_path(self) -> None:
        """Save with special characters in path (spaces, unicode)."""
        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            config_path.touch()

            # Path with spaces
            save_dir = Path(tmpdir) / "My Documents"
            save_dir.mkdir()
            save_bookmark(config_path, path=save_dir, name="docs")
            entries = read_config(config_path)
            assert entries[0].path == save_dir

    def test_save_with_relative_path(self) -> None:
        """Save with relative path (must resolve to absolute)."""
        import os

        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            config_path.touch()

            save_dir = Path(tmpdir) / "project"
            save_dir.mkdir()
            save_dir_resolved = save_dir.resolve()

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                save_bookmark(config_path, path=Path("project"), name="proj")

                entries = read_config(config_path)
                assert entries[0].path == save_dir_resolved
                assert entries[0].path.is_absolute()
            finally:
                os.chdir(original_cwd)

    def test_reject_duplicate_name(self) -> None:
        """Reject duplicate name with clear error message."""
        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            # Save first entry
            write_config(config_path, [
                BookmarkEntry(name="proj", depth=0, path=dir1)
            ])

            # Try to save duplicate name
            with pytest.raises(ValueError, match="name 'proj' already exists"):
                save_bookmark(config_path, path=dir2, name="proj")

    def test_reject_duplicate_path(self) -> None:
        """Reject duplicate path with error identifying existing entry."""
        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            save_dir = Path(tmpdir) / "project"
            save_dir.mkdir()

            # Save first entry
            write_config(config_path, [
                BookmarkEntry(name="proj1", depth=0, path=save_dir)
            ])

            # Try to save duplicate path
            with pytest.raises(ValueError, match="path .* already saved under name 'proj1'"):
                save_bookmark(config_path, path=save_dir, name="proj2")

    def test_reject_invalid_depth(self) -> None:
        """Reject depth outside 0-10 range."""
        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            config_path.touch()
            save_dir = Path(tmpdir) / "test"
            save_dir.mkdir()

            # Negative depth
            with pytest.raises(ValueError, match="Depth must be"):
                save_bookmark(config_path, path=save_dir, depth=-1, name="test")

            # Depth > 10
            with pytest.raises(ValueError, match="Depth must be"):
                save_bookmark(config_path, path=save_dir, depth=11, name="test")

    def test_reject_nonexistent_path(self) -> None:
        """Reject path that does not exist on disk."""
        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            config_path.touch()

            nonexistent = Path(tmpdir) / "does-not-exist"

            with pytest.raises(ValueError, match="does not exist"):
                save_bookmark(config_path, path=nonexistent, name="test")

    def test_reject_file_path(self) -> None:
        """Reject path that is a file, not a directory."""
        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            config_path.touch()

            file_path = Path(tmpdir) / "afile.txt"
            file_path.touch()

            with pytest.raises(ValueError, match="not a directory"):
                save_bookmark(config_path, path=file_path, name="test")

    def test_config_auto_created_when_missing(self) -> None:
        """Config is auto-created when saving to a missing config file."""
        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.rc"
            save_dir = Path(tmpdir) / "test"
            save_dir.mkdir()

            save_bookmark(config_path, path=save_dir, name="test")

            assert config_path.exists()
            entries = read_config(config_path)
            assert len(entries) == 1
            assert entries[0].name == "test"

    def test_config_corrupted_error(self) -> None:
        """Config corrupted produces clear error."""
        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            config_path.write_text("corrupted line\n")

            save_dir = Path(tmpdir) / "test"
            save_dir.mkdir()

            with pytest.raises(ValueError, match="Failed to parse"):
                save_bookmark(config_path, path=save_dir, name="test")

    def test_save_preserves_comment_header(self) -> None:
        """Comment header is preserved after saving a bookmark."""
        from dirq.config import save_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            header = "# my custom header\n# second line\n"
            config_path.write_text(header)

            save_dir = Path(tmpdir) / "test"
            save_dir.mkdir()

            save_bookmark(config_path, path=save_dir, name="test")

            content = config_path.read_text()
            assert content.startswith(header)
            assert "test\t0\t" in content


class TestDeleteBookmark:
    """Test delete bookmark functionality."""

    def test_delete_by_exact_name_match(self) -> None:
        """Delete by exact name match."""
        from dirq.config import delete_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            # Create config with two entries
            write_config(config_path, [
                BookmarkEntry(name="proj1", depth=0, path=dir1),
                BookmarkEntry(name="proj2", depth=0, path=dir2),
            ])

            result = delete_bookmark(config_path, "proj1")

            # Verify proj1 is deleted
            entries = read_config(config_path)
            assert len(entries) == 1
            assert entries[0].name == "proj2"
            assert "Deleted 'proj1'" in result

    def test_delete_by_exact_path_match(self) -> None:
        """Delete by exact path match."""
        from dirq.config import delete_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            # Create config with two entries
            write_config(config_path, [
                BookmarkEntry(name="proj1", depth=0, path=dir1),
                BookmarkEntry(name="proj2", depth=0, path=dir2),
            ])

            result = delete_bookmark(config_path, str(dir1))

            # Verify entry with dir1 path is deleted
            entries = read_config(config_path)
            assert len(entries) == 1
            assert entries[0].name == "proj2"
            assert "Deleted 'proj1'" in result

    def test_name_match_takes_priority_over_path(self) -> None:
        """Name match takes priority over path match."""
        from dirq.config import delete_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            dir1 = Path(tmpdir) / "dir1"
            dir2 = Path(tmpdir) / "dir2"
            dir1.mkdir()
            dir2.mkdir()

            # Create entry where name matches a path
            write_config(config_path, [
                BookmarkEntry(name=str(dir2), depth=0, path=dir1),
                BookmarkEntry(name="proj2", depth=0, path=dir2),
            ])

            # Delete by str(dir2) - should match by name first
            delete_bookmark(config_path, str(dir2))

            entries = read_config(config_path)
            assert len(entries) == 1
            # Should have deleted the entry with name=str(dir2), leaving proj2
            assert entries[0].name == "proj2"

    def test_no_matching_entry_produces_error(self) -> None:
        """No matching entry produces error."""
        from dirq.config import delete_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            dir1 = Path(tmpdir) / "dir1"
            dir1.mkdir()

            write_config(config_path, [
                BookmarkEntry(name="proj1", depth=0, path=dir1),
            ])

            with pytest.raises(ValueError, match="no bookmark found matching 'nonexistent'"):
                delete_bookmark(config_path, "nonexistent")

    def test_delete_config_missing_error(self) -> None:
        """Config missing produces clear error."""
        from dirq.config import delete_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.rc"

            with pytest.raises(FileNotFoundError, match="Config file not found"):
                delete_bookmark(config_path, "test")

    def test_delete_config_corrupted_error(self) -> None:
        """Config corrupted produces clear error."""
        from dirq.config import delete_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            config_path.write_text("corrupted line\n")

            with pytest.raises(ValueError, match="Failed to parse"):
                delete_bookmark(config_path, "test")

    def test_delete_preserves_comment_header(self) -> None:
        """Comment header is preserved after deleting a bookmark."""
        from dirq.config import delete_bookmark

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.rc"
            dir1 = Path(tmpdir) / "dir1"
            dir1.mkdir()

            header = "# custom comment\n# another line\n"
            config_path.write_text(header + f"proj1\t0\t{dir1}\n")

            delete_bookmark(config_path, "proj1")

            content = config_path.read_text()
            assert content.startswith(header)
