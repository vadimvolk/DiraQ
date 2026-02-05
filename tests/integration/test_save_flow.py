"""Integration tests for save and delete flows."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path


class TestSaveFlow:
    """Test end-to-end save flow."""

    def test_save_with_defaults(self) -> None:
        """dirq save with defaults (cwd, depth 0, basename)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch()

            env = os.environ.copy()
            env["XDG_CONFIG_HOME"] = tmpdir

            # Create a test directory and save from there
            test_dir = Path(tmpdir) / "myproject"
            test_dir.mkdir()

            result = subprocess.run(
                [sys.executable, "-m", "dirq", "save"],
                capture_output=True,
                text=True,
                cwd=str(test_dir),
                env=env,
            )

            assert result.returncode == 0
            assert "Saved 'myproject'" in result.stdout
            assert str(test_dir) in result.stdout
            assert "(depth: 0)" in result.stdout

            # Verify config file
            content = config_path.read_text()
            assert "myproject\t0\t" in content

    def test_save_with_explicit_args(self) -> None:
        """dirq save with explicit path, depth, and name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch()

            env = os.environ.copy()
            env["XDG_CONFIG_HOME"] = tmpdir

            test_dir = Path(tmpdir) / "repos"
            test_dir.mkdir()

            result = subprocess.run(
                [sys.executable, "-m", "dirq", "save", str(test_dir), "2", "myrepos"],
                capture_output=True,
                text=True,
                env=env,
            )

            assert result.returncode == 0
            assert "Saved 'myrepos'" in result.stdout
            assert "(depth: 2)" in result.stdout

            # Verify config file
            content = config_path.read_text()
            assert "myrepos\t2\t" in content

    def test_duplicate_name_rejection(self) -> None:
        """dirq save rejects duplicate name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Create initial entry
            dir1 = Path(tmpdir) / "dir1"
            dir1.mkdir()
            config_path.write_text(f"proj\t0\t{dir1}\n")

            env = os.environ.copy()
            env["XDG_CONFIG_HOME"] = tmpdir

            # Try to save with duplicate name
            dir2 = Path(tmpdir) / "dir2"
            dir2.mkdir()

            result = subprocess.run(
                [sys.executable, "-m", "dirq", "save", str(dir2), "0", "proj"],
                capture_output=True,
                text=True,
                env=env,
            )

            assert result.returncode == 2
            assert "error: name 'proj' already exists" in result.stderr

    def test_duplicate_path_rejection(self) -> None:
        """dirq save rejects duplicate path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Create initial entry
            test_dir = Path(tmpdir) / "project"
            test_dir.mkdir()
            config_path.write_text(f"proj1\t0\t{test_dir}\n")

            env = os.environ.copy()
            env["XDG_CONFIG_HOME"] = tmpdir

            # Try to save with duplicate path
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "save", str(test_dir), "0", "proj2"],
                capture_output=True,
                text=True,
                env=env,
            )

            assert result.returncode == 2
            assert "already saved under name 'proj1'" in result.stderr

    def test_save_confirmation_format(self) -> None:
        """Verify save confirmation message format per contract."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch()

            env = os.environ.copy()
            env["XDG_CONFIG_HOME"] = tmpdir

            test_dir = Path(tmpdir) / "repos"
            test_dir.mkdir()

            result = subprocess.run(
                [sys.executable, "-m", "dirq", "save", str(test_dir), "2", "repos"],
                capture_output=True,
                text=True,
                env=env,
            )

            assert result.returncode == 0
            # Format: Saved 'repos' -> /path/to/repos (depth: 2)
            assert "Saved 'repos' ->" in result.stdout
            assert str(test_dir) in result.stdout
            assert "(depth: 2)" in result.stdout

    def test_save_exit_codes(self) -> None:
        """Verify save exit codes match contract."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch()

            env = os.environ.copy()
            env["XDG_CONFIG_HOME"] = tmpdir

            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()

            # Success case
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "save", str(test_dir), "0", "test"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 0

            # Error case: duplicate name
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "save", str(test_dir), "0", "test"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 2


class TestDeleteFlow:
    """Test end-to-end delete flow."""

    def test_save_then_delete_by_name(self) -> None:
        """Save a bookmark then delete it by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch()

            env = os.environ.copy()
            env["XDG_CONFIG_HOME"] = tmpdir

            test_dir = Path(tmpdir) / "project"
            test_dir.mkdir()

            # Save
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "save", str(test_dir), "0", "proj"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 0

            # Delete by name
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "delete", "proj"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 0
            assert "Deleted 'proj'" in result.stdout

            # Verify config is empty
            content = config_path.read_text().strip()
            assert content == ""

    def test_save_then_delete_by_path(self) -> None:
        """Save a bookmark then delete it by path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch()

            env = os.environ.copy()
            env["XDG_CONFIG_HOME"] = tmpdir

            test_dir = Path(tmpdir) / "project"
            test_dir.mkdir()
            test_dir_resolved = test_dir.resolve()

            # Save (paths get resolved)
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "save", str(test_dir_resolved), "0", "proj"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 0

            # Delete by path (use the same resolved path)
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "delete", str(test_dir_resolved)],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 0
            assert "Deleted 'proj'" in result.stdout

    def test_delete_nonexistent_entry(self) -> None:
        """Delete nonexistent entry produces error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch()

            env = os.environ.copy()
            env["XDG_CONFIG_HOME"] = tmpdir

            result = subprocess.run(
                [sys.executable, "-m", "dirq", "delete", "nonexistent"],
                capture_output=True,
                text=True,
                env=env,
            )

            assert result.returncode == 2
            assert "error:" in result.stderr
            assert "no bookmark found" in result.stderr

    def test_delete_confirmation_format(self) -> None:
        """Verify delete confirmation message format per contract."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)

            test_dir = Path(tmpdir) / "repos"
            test_dir.mkdir()

            # Save first
            config_path.write_text(f"repos\t0\t{test_dir}\n")

            env = os.environ.copy()
            env["XDG_CONFIG_HOME"] = tmpdir

            # Delete
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "delete", "repos"],
                capture_output=True,
                text=True,
                env=env,
            )

            assert result.returncode == 0
            assert "Deleted 'repos'" in result.stdout

    def test_delete_exit_codes(self) -> None:
        """Verify delete exit codes match contract."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)

            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            config_path.write_text(f"test\t0\t{test_dir}\n")

            env = os.environ.copy()
            env["XDG_CONFIG_HOME"] = tmpdir

            # Success case
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "delete", "test"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 0

            # Error case: nonexistent
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "delete", "nonexistent"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 2
