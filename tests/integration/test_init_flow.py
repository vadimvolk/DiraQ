"""Integration tests for init config and init shell flows."""
import subprocess
import sys
import tempfile
from pathlib import Path


class TestInitConfigFlow:
    """Test end-to-end init config flow."""

    def test_init_config_creates_file(self) -> None:
        """dirq init config creates file at expected location."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            env = {"XDG_CONFIG_HOME": tmpdir}

            result = subprocess.run(
                [sys.executable, "-m", "dirq", "init", "config"],
                capture_output=True,
                text=True,
                env=env,
            )

            assert result.returncode == 0
            assert config_path.exists()
            assert f"Created config at {config_path}" in result.stdout

    def test_init_config_already_exists(self) -> None:
        """Running init config again reports already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "dirq" / "config.rc"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text("existing\t0\t/existing\n")

            env = {"XDG_CONFIG_HOME": tmpdir}

            result = subprocess.run(
                [sys.executable, "-m", "dirq", "init", "config"],
                capture_output=True,
                text=True,
                env=env,
            )

            assert result.returncode == 0
            assert f"Config already exists at {config_path}" in result.stderr
            # Content should be preserved
            content = config_path.read_text()
            assert "existing\t0\t/existing" in content

    def test_init_config_exit_codes(self) -> None:
        """Verify init config exit codes match contract."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"XDG_CONFIG_HOME": tmpdir}

            # Success case
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "init", "config"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 0

            # Already exists case (should still be 0)
            result = subprocess.run(
                [sys.executable, "-m", "dirq", "init", "config"],
                capture_output=True,
                text=True,
                env=env,
            )
            assert result.returncode == 0


class TestInitShellFlow:
    """Test end-to-end init shell flow."""

    def test_init_shell_fish_outputs_valid_script(self) -> None:
        """dirq init shell fish installs completion and wrapper."""
        result = subprocess.run(
            [sys.executable, "-m", "dirq", "init", "shell", "fish"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Installed fish completion:" in result.stdout
        assert "Installed fish wrapper:" in result.stdout
        assert ".config/fish/completions/dirq.fish" in result.stdout
        assert ".config/fish/functions/dirq.fish" in result.stdout

    def test_init_shell_bash_outputs_valid_script(self) -> None:
        """dirq init shell bash installs completion and wrapper."""
        result = subprocess.run(
            [sys.executable, "-m", "dirq", "init", "shell", "bash"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Installed bash completion:" in result.stdout
        assert "Installed bash wrapper:" in result.stdout
        assert ".bash_completion.d/dirq" in result.stdout
        assert ".bash_completion.d/dirq-wrapper" in result.stdout

    def test_init_shell_zsh_outputs_valid_script(self) -> None:
        """dirq init shell zsh installs completion and wrapper."""
        result = subprocess.run(
            [sys.executable, "-m", "dirq", "init", "shell", "zsh"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Installed zsh completion:" in result.stdout
        assert "Installed zsh wrapper:" in result.stdout
        assert ".zsh/completions/_dirq" in result.stdout
        assert ".zsh/functions/dirq-wrapper" in result.stdout

    def test_init_shell_unsupported_produces_error(self) -> None:
        """dirq init shell nush produces error with supported shell list."""
        result = subprocess.run(
            [sys.executable, "-m", "dirq", "init", "shell", "nush"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 2
        assert "error:" in result.stderr
        assert "invalid" in result.stderr.lower() or "unsupported" in result.stderr.lower()

    def test_init_shell_exit_codes(self) -> None:
        """Verify init shell exit codes per contract."""
        # Success case
        result = subprocess.run(
            [sys.executable, "-m", "dirq", "init", "shell", "fish"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

        # Error case: unsupported shell
        result = subprocess.run(
            [sys.executable, "-m", "dirq", "init", "shell", "invalid"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2
