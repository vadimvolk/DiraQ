"""Tests for navigation functionality."""
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from dirq.config import BookmarkEntry


class TestFolderScanning:
    """Test folder scanning with different depths."""

    def test_depth_0_returns_just_root(self) -> None:
        """Depth 0 returns just the root path."""
        from dirq.navigator import scan_folders

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Create some subdirectories
            (root / "sub1").mkdir()
            (root / "sub2").mkdir()

            result = scan_folders(root, 0)
            assert result == [root]

    def test_depth_1_returns_direct_subdirectories(self) -> None:
        """Depth 1 returns direct subdirectories."""
        from dirq.navigator import scan_folders

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            sub1 = root / "sub1"
            sub2 = root / "sub2"
            sub1.mkdir()
            sub2.mkdir()
            # Create nested subdirs that shouldn't be included
            (sub1 / "nested").mkdir()

            result = scan_folders(root, 1)
            assert set(result) == {sub1, sub2}

    def test_depth_2_returns_subdirectories_up_to_2_levels(self) -> None:
        """Depth 2 returns subdirectories up to 2 levels deep."""
        from dirq.navigator import scan_folders

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            sub1 = root / "sub1"
            sub2 = root / "sub2"
            nested1 = sub1 / "nested1"
            nested2 = sub1 / "nested2"
            sub1.mkdir()
            sub2.mkdir()
            nested1.mkdir()
            nested2.mkdir()
            # Level 3 that shouldn't be included
            (nested1 / "deep").mkdir()

            result = scan_folders(root, 2)
            assert set(result) == {sub1, sub2, nested1, nested2}

    def test_non_existent_root_returns_empty(self) -> None:
        """Non-existent root path returns empty list."""
        from dirq.navigator import scan_folders

        result = scan_folders(Path("/nonexistent/path"), 1)
        assert result == []

    def test_handles_permission_errors(self) -> None:
        """Handles permission errors gracefully (skip inaccessible dirs)."""
        from dirq.navigator import scan_folders

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            accessible = root / "accessible"
            accessible.mkdir()

            # We can scan without errors
            result = scan_folders(root, 1)
            assert accessible in result

    def test_ignores_files(self) -> None:
        """Ignores files, only returns directories."""
        from dirq.navigator import scan_folders

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            subdir = root / "subdir"
            subdir.mkdir()
            (root / "file.txt").touch()
            (subdir / "another_file.txt").touch()

            result = scan_folders(root, 1)
            assert result == [subdir]


class TestFilterIntermediateFolders:
    """Test filtering of intermediate pass-through folders."""

    def test_leaf_folders_kept(self) -> None:
        """Leaf folders (no subdirectories) are always kept."""
        from dirq.navigator import filter_intermediate_folders

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            leaf1 = root / "leaf1"
            leaf2 = root / "leaf2"
            leaf1.mkdir()
            leaf2.mkdir()

            result = filter_intermediate_folders([leaf1, leaf2])
            assert set(result) == {leaf1, leaf2}

    def test_intermediate_folder_without_files_filtered(self) -> None:
        """Intermediate folder with all subdirs in list and no files is filtered out."""
        from dirq.navigator import filter_intermediate_folders

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parent = root / "parent"
            child1 = parent / "child1"
            child2 = parent / "child2"
            parent.mkdir()
            child1.mkdir()
            child2.mkdir()

            # parent has subdirs child1 and child2, both in the list, no files
            result = filter_intermediate_folders([parent, child1, child2])
            assert set(result) == {child1, child2}

    def test_intermediate_folder_with_files_kept(self) -> None:
        """Intermediate folder with files is kept even if all subdirs are in list."""
        from dirq.navigator import filter_intermediate_folders

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parent = root / "parent"
            child1 = parent / "child1"
            child2 = parent / "child2"
            parent.mkdir()
            child1.mkdir()
            child2.mkdir()
            (parent / "README.md").touch()

            result = filter_intermediate_folders([parent, child1, child2])
            assert set(result) == {parent, child1, child2}

    def test_folder_with_partial_subdirs_in_list_kept(self) -> None:
        """Folder is kept if not all its subdirs are in the list."""
        from dirq.navigator import filter_intermediate_folders

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parent = root / "parent"
            child1 = parent / "child1"
            child2 = parent / "child2"
            parent.mkdir()
            child1.mkdir()
            child2.mkdir()

            # Only child1 in list, child2 not included
            result = filter_intermediate_folders([parent, child1])
            assert set(result) == {parent, child1}

    def test_empty_folder_kept(self) -> None:
        """Empty folder (no files, no subdirs) is kept."""
        from dirq.navigator import filter_intermediate_folders

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            empty = root / "empty"
            empty.mkdir()

            result = filter_intermediate_folders([empty])
            assert result == [empty]

    def test_multi_level_filtering(self) -> None:
        """Multi-level tree filters all pass-through intermediates."""
        from dirq.navigator import filter_intermediate_folders

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # sources/ergohaven/fw, sources/ergohaven/hw, sources/vadimvolk/repo1
            ergo = root / "ergohaven"
            fw = ergo / "fw"
            hw = ergo / "hw"
            vadim = root / "vadimvolk"
            repo1 = vadim / "repo1"
            for d in [ergo, fw, hw, vadim, repo1]:
                d.mkdir(parents=True)

            folders = [ergo, fw, hw, vadim, repo1]
            result = filter_intermediate_folders(folders)
            # Both ergo and vadim are pass-through (no files, all subdirs present)
            assert set(result) == {fw, hw, repo1}


class TestNavigationListBuilding:
    """Test navigation list building and display formatting."""

    def test_depth_0_formats_as_name_colon_full_path(self) -> None:
        """Depth 0 formats as 'name:/full/path'."""
        from dirq.navigator import build_navigation_list

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            entries = [BookmarkEntry(name="proj", depth=0, path=root)]

            nav_entries, warnings = build_navigation_list(entries, None, None)

            assert len(nav_entries) == 1
            assert nav_entries[0]["display"] == f"proj:{root}"
            assert nav_entries[0]["absolute_path"] == root
            assert nav_entries[0]["source_name"] == "proj"
            assert warnings == []

    def test_depth_n_formats_as_name_colon_relative_path(self) -> None:
        """Depth N formats as 'name:<relative-path>'."""
        from dirq.navigator import build_navigation_list

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            sub1 = root / "sub1"
            sub2 = root / "sub2"
            sub1.mkdir()
            sub2.mkdir()

            entries = [BookmarkEntry(name="repos", depth=1, path=root)]

            nav_entries, warnings = build_navigation_list(entries, None, None)

            # Should have entries for sub1 and sub2
            assert len(nav_entries) == 2
            displays = {e["display"] for e in nav_entries}
            assert "repos:sub1" in displays
            assert "repos:sub2" in displays
            assert warnings == []

    def test_only_filter_includes_only_specified_names(self) -> None:
        """--only filtering includes only specified bookmark names."""
        from dirq.navigator import build_navigation_list

        with tempfile.TemporaryDirectory() as tmpdir:
            root1 = Path(tmpdir) / "proj1"
            root2 = Path(tmpdir) / "proj2"
            root3 = Path(tmpdir) / "proj3"
            root1.mkdir()
            root2.mkdir()
            root3.mkdir()

            entries = [
                BookmarkEntry(name="proj1", depth=0, path=root1),
                BookmarkEntry(name="proj2", depth=0, path=root2),
                BookmarkEntry(name="proj3", depth=0, path=root3),
            ]

            nav_entries, warnings = build_navigation_list(
                entries, only=["proj1", "proj3"], except_names=None
            )

            assert len(nav_entries) == 2
            names = {e["source_name"] for e in nav_entries}
            assert names == {"proj1", "proj3"}

    def test_except_filter_excludes_specified_names(self) -> None:
        """--except filtering excludes specified bookmark names."""
        from dirq.navigator import build_navigation_list

        with tempfile.TemporaryDirectory() as tmpdir:
            root1 = Path(tmpdir) / "proj1"
            root2 = Path(tmpdir) / "proj2"
            root3 = Path(tmpdir) / "proj3"
            root1.mkdir()
            root2.mkdir()
            root3.mkdir()

            entries = [
                BookmarkEntry(name="proj1", depth=0, path=root1),
                BookmarkEntry(name="proj2", depth=0, path=root2),
                BookmarkEntry(name="proj3", depth=0, path=root3),
            ]

            nav_entries, warnings = build_navigation_list(
                entries, only=None, except_names=["proj2"]
            )

            assert len(nav_entries) == 2
            names = {e["source_name"] for e in nav_entries}
            assert names == {"proj1", "proj3"}

    def test_only_and_except_mutual_exclusion(self) -> None:
        """--only + --except mutual exclusion raises error."""
        from dirq.navigator import build_navigation_list

        entries = [BookmarkEntry(name="test", depth=0, path=Path("/test"))]

        with pytest.raises(ValueError, match="--only and --except are mutually exclusive"):
            build_navigation_list(entries, only=["test"], except_names=["other"])

    def test_only_with_nonexistent_name_raises_error(self) -> None:
        """--only with nonexistent bookmark name raises error."""
        from dirq.navigator import build_navigation_list

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            entries = [BookmarkEntry(name="existing", depth=0, path=root)]

            with pytest.raises(ValueError, match="bookmark 'nonexistent' not found"):
                build_navigation_list(entries, only=["nonexistent"], except_names=None)

    def test_missing_folders_produce_warnings(self) -> None:
        """Missing folders produce warnings and are skipped."""
        from dirq.navigator import build_navigation_list

        with tempfile.TemporaryDirectory() as tmpdir:
            existing = Path(tmpdir) / "existing"
            existing.mkdir()
            missing = Path("/nonexistent/path")

            entries = [
                BookmarkEntry(name="good", depth=0, path=existing),
                BookmarkEntry(name="bad", depth=0, path=missing),
            ]

            nav_entries, warnings = build_navigation_list(entries, None, None)

            assert len(nav_entries) == 1
            assert nav_entries[0]["source_name"] == "good"
            assert len(warnings) == 1
            assert "bad" in warnings[0]
            assert str(missing) in warnings[0]

    def test_all_folders_missing_produces_error(self) -> None:
        """All folders missing produces error."""
        from dirq.navigator import build_navigation_list

        entries = [
            BookmarkEntry(name="bad1", depth=0, path=Path("/nonexistent1")),
            BookmarkEntry(name="bad2", depth=0, path=Path("/nonexistent2")),
        ]

        with pytest.raises(ValueError, match="no valid bookmark folders found"):
            build_navigation_list(entries, None, None)

    def test_empty_config_produces_helpful_message(self) -> None:
        """Empty config produces helpful error message."""
        from dirq.navigator import build_navigation_list

        with pytest.raises(ValueError, match="no bookmarks in config.*dirq save"):
            build_navigation_list([], None, None)

    def test_depth_n_filters_intermediate_folders(self) -> None:
        """Depth N filters out intermediate pass-through folders."""
        from dirq.navigator import build_navigation_list

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            parent = root / "parent"
            child1 = parent / "child1"
            child2 = parent / "child2"
            parent.mkdir()
            child1.mkdir()
            child2.mkdir()

            entries = [BookmarkEntry(name="src", depth=2, path=root)]

            nav_entries, warnings = build_navigation_list(entries, None, None)

            displays = {e["display"] for e in nav_entries}
            # parent is filtered out (no files, all subdirs present)
            assert "src:parent/child1" in displays
            assert "src:parent/child2" in displays
            assert "src:parent" not in displays
            assert warnings == []

    def test_depth_0_empty_folder_displayed(self) -> None:
        """Empty folder with depth 0 is always displayed."""
        from dirq.navigator import build_navigation_list

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            empty = root / "empty"
            empty.mkdir()

            entries = [BookmarkEntry(name="empty", depth=0, path=empty)]

            nav_entries, warnings = build_navigation_list(entries, None, None)

            assert len(nav_entries) == 1
            assert nav_entries[0]["display"] == f"empty:{empty}"
            assert warnings == []

    def test_special_characters_in_paths(self) -> None:
        """Special characters in paths are handled correctly."""
        from dirq.navigator import build_navigation_list

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "My Documents"
            root.mkdir()

            entries = [BookmarkEntry(name="docs", depth=0, path=root)]

            nav_entries, warnings = build_navigation_list(entries, None, None)

            assert len(nav_entries) == 1
            assert nav_entries[0]["absolute_path"] == root
            assert warnings == []


class TestFzfIntegration:
    """Test fzf integration."""

    def test_fzf_not_installed_produces_clear_error(self) -> None:
        """fzf not installed produces clear error."""
        from dirq.navigator import run_fzf

        nav_entries = [{"display": "test:/path", "absolute_path": Path("/path")}]

        with mock.patch("subprocess.run", side_effect=FileNotFoundError()):
            with pytest.raises(FileNotFoundError, match="fzf"):
                run_fzf(nav_entries)

    def test_fzf_receives_correct_input(self) -> None:
        """fzf receives correct input (piped navigation list)."""
        from dirq.navigator import run_fzf

        nav_entries = [
            {"display": "proj1:/path1", "absolute_path": Path("/path1")},
            {"display": "proj2:/path2", "absolute_path": Path("/path2")},
        ]

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=0, stdout="proj1:/path1")
            run_fzf(nav_entries)

            # Verify subprocess.run was called with correct input
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args[1]
            assert "proj1:/path1\nproj2:/path2" in call_kwargs["input"]

    def test_fzf_exit_code_0_returns_selected_path(self) -> None:
        """fzf exit code 0 returns selected absolute path."""
        from dirq.navigator import run_fzf

        nav_entries = [{"display": "proj:/path", "absolute_path": Path("/path")}]

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=0, stdout="proj:/path")
            result = run_fzf(nav_entries)

            assert result == Path("/path")

    def test_fzf_exit_code_1_returns_none(self) -> None:
        """fzf exit code 1 (no match/Ctrl+C) returns None."""
        from dirq.navigator import run_fzf

        nav_entries = [{"display": "proj:/path", "absolute_path": Path("/path")}]

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=1, stdout="")
            result = run_fzf(nav_entries)

            assert result is None

    def test_fzf_exit_code_130_returns_none(self) -> None:
        """fzf exit code 130 (Ctrl+C) returns None."""
        from dirq.navigator import run_fzf

        nav_entries = [{"display": "proj:/path", "absolute_path": Path("/path")}]

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=130, stdout="")
            result = run_fzf(nav_entries)

            assert result is None

    def test_parse_fzf_output_extracts_absolute_path(self) -> None:
        """Parse fzf output to extract absolute path from display format."""
        from dirq.navigator import run_fzf

        nav_entries = [
            {"display": "repos:sub1", "absolute_path": Path("/opt/repos/sub1")},
            {"display": "repos:sub2", "absolute_path": Path("/opt/repos/sub2")},
        ]

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=0, stdout="repos:sub1")
            result = run_fzf(nav_entries)

            assert result == Path("/opt/repos/sub1")
