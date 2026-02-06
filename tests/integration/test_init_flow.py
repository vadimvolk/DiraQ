"""Integration tests for init config and init shell flows."""
import os
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


def _make_shell_env(home: str) -> dict[str, str]:
    """Create subprocess env with HOME redirected to a temp directory."""
    env = os.environ.copy()
    env["HOME"] = home
    return env


def _run_init_shell(shell: str, home: str) -> subprocess.CompletedProcess[str]:
    """Run dirq init shell <shell> with HOME redirected."""
    return subprocess.run(
        [sys.executable, "-m", "dirq", "init", "shell", shell],
        capture_output=True,
        text=True,
        env=_make_shell_env(home),
    )


class TestInitShellFish:
    """End-to-end tests for dirq init shell fish."""

    def test_creates_completion_file(self) -> None:
        """Completion file is created at ~/.config/fish/completions/dirq.fish."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("fish", home)

            assert result.returncode == 0
            completion = Path(home) / ".config" / "fish" / "completions" / "dirq.fish"
            assert completion.exists()

    def test_creates_wrapper_file(self) -> None:
        """Wrapper file is created at ~/.config/fish/functions/dirq.fish."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("fish", home)

            assert result.returncode == 0
            wrapper = Path(home) / ".config" / "fish" / "functions" / "dirq.fish"
            assert wrapper.exists()

    def test_completion_contains_valid_fish_completions(self) -> None:
        """Installed completion file has fish complete commands for all subcommands."""
        with tempfile.TemporaryDirectory() as home:
            _run_init_shell("fish", home)
            content = (Path(home) / ".config/fish/completions/dirq.fish").read_text()

            assert "complete -c dirq" in content
            assert "navigate" in content
            assert "save" in content
            assert "delete" in content
            assert "init" in content

    def test_wrapper_contains_cd_function(self) -> None:
        """Installed wrapper file defines a dirq function that cd's on navigate."""
        with tempfile.TemporaryDirectory() as home:
            _run_init_shell("fish", home)
            content = (Path(home) / ".config/fish/functions/dirq.fish").read_text()

            assert "function dirq" in content
            assert "command dirq navigate" in content
            assert "cd" in content

    def test_output_mentions_installed_paths(self) -> None:
        """CLI output confirms both files were installed."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("fish", home)

            assert "Installed fish completion:" in result.stdout
            assert "Installed fish wrapper:" in result.stdout
            assert ".config/fish/completions/dirq.fish" in result.stdout
            assert ".config/fish/functions/dirq.fish" in result.stdout

    def test_output_says_auto_load(self) -> None:
        """Fish instructions say files are automatically loaded."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("fish", home)

            assert "automatically load" in result.stdout.lower()

    def test_creates_parent_directories(self) -> None:
        """Parent directories are created even when they don't exist."""
        with tempfile.TemporaryDirectory() as home:
            # Verify no fish dirs exist yet
            assert not (Path(home) / ".config" / "fish").exists()

            result = _run_init_shell("fish", home)

            assert result.returncode == 0
            assert (Path(home) / ".config" / "fish" / "completions").is_dir()
            assert (Path(home) / ".config" / "fish" / "functions").is_dir()

    def test_idempotent_reinstall(self) -> None:
        """Running init shell fish twice succeeds and updates files."""
        with tempfile.TemporaryDirectory() as home:
            result1 = _run_init_shell("fish", home)
            result2 = _run_init_shell("fish", home)

            assert result1.returncode == 0
            assert result2.returncode == 0

            # Files still exist with correct content
            completion = Path(home) / ".config/fish/completions/dirq.fish"
            wrapper = Path(home) / ".config/fish/functions/dirq.fish"
            assert "complete -c dirq" in completion.read_text()
            assert "function dirq" in wrapper.read_text()


class TestInitShellBash:
    """End-to-end tests for dirq init shell bash."""

    def test_creates_completion_file(self) -> None:
        """Completion file is created at ~/.bash_completion.d/dirq."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("bash", home)

            assert result.returncode == 0
            completion = Path(home) / ".bash_completion.d" / "dirq"
            assert completion.exists()

    def test_creates_wrapper_file(self) -> None:
        """Wrapper file is created at ~/.bash_completion.d/dirq-wrapper."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("bash", home)

            assert result.returncode == 0
            wrapper = Path(home) / ".bash_completion.d" / "dirq-wrapper"
            assert wrapper.exists()

    def test_completion_contains_valid_bash_completions(self) -> None:
        """Installed completion file has bash complete function for all subcommands."""
        with tempfile.TemporaryDirectory() as home:
            _run_init_shell("bash", home)
            content = (Path(home) / ".bash_completion.d/dirq").read_text()

            assert "_dirq_completions" in content
            assert "complete -F" in content
            assert "navigate" in content
            assert "save" in content
            assert "delete" in content
            assert "init" in content

    def test_wrapper_contains_cd_function(self) -> None:
        """Installed wrapper file defines a dirq function that cd's on navigate."""
        with tempfile.TemporaryDirectory() as home:
            _run_init_shell("bash", home)
            content = (Path(home) / ".bash_completion.d/dirq-wrapper").read_text()

            assert "dirq()" in content
            assert "command dirq navigate" in content
            assert "cd" in content

    def test_output_mentions_installed_paths(self) -> None:
        """CLI output confirms both files were installed."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("bash", home)

            assert "Installed bash completion:" in result.stdout
            assert "Installed bash wrapper:" in result.stdout

    def test_output_mentions_bashrc_sourcing(self) -> None:
        """Bash instructions mention sourcing from ~/.bashrc."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("bash", home)

            assert "~/.bashrc" in result.stdout
            assert "source" in result.stdout

    def test_idempotent_reinstall(self) -> None:
        """Running init shell bash twice succeeds and updates files."""
        with tempfile.TemporaryDirectory() as home:
            result1 = _run_init_shell("bash", home)
            result2 = _run_init_shell("bash", home)

            assert result1.returncode == 0
            assert result2.returncode == 0

            completion = Path(home) / ".bash_completion.d/dirq"
            wrapper = Path(home) / ".bash_completion.d/dirq-wrapper"
            assert "_dirq_completions" in completion.read_text()
            assert "dirq()" in wrapper.read_text()


class TestInitShellZsh:
    """End-to-end tests for dirq init shell zsh."""

    def test_creates_completion_file(self) -> None:
        """Completion file is created at ~/.zsh/completions/_dirq."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("zsh", home)

            assert result.returncode == 0
            completion = Path(home) / ".zsh" / "completions" / "_dirq"
            assert completion.exists()

    def test_creates_wrapper_file(self) -> None:
        """Wrapper file is created at ~/.zsh/functions/dirq-wrapper."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("zsh", home)

            assert result.returncode == 0
            wrapper = Path(home) / ".zsh" / "functions" / "dirq-wrapper"
            assert wrapper.exists()

    def test_completion_contains_valid_zsh_completions(self) -> None:
        """Installed completion file has zsh compdef setup for all subcommands."""
        with tempfile.TemporaryDirectory() as home:
            _run_init_shell("zsh", home)
            content = (Path(home) / ".zsh/completions/_dirq").read_text()

            assert "#compdef dirq" in content
            assert "_dirq()" in content or "_dirq " in content
            assert "navigate" in content
            assert "save" in content
            assert "delete" in content
            assert "init" in content

    def test_wrapper_contains_cd_function(self) -> None:
        """Installed wrapper file defines a dirq function that cd's on navigate."""
        with tempfile.TemporaryDirectory() as home:
            _run_init_shell("zsh", home)
            content = (Path(home) / ".zsh/functions/dirq-wrapper").read_text()

            assert "dirq()" in content
            assert "command dirq navigate" in content
            assert "cd" in content

    def test_output_mentions_installed_paths(self) -> None:
        """CLI output confirms both files were installed."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("zsh", home)

            assert "Installed zsh completion:" in result.stdout
            assert "Installed zsh wrapper:" in result.stdout

    def test_output_mentions_zshrc_setup(self) -> None:
        """Zsh instructions mention fpath and compinit setup in ~/.zshrc."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("zsh", home)

            assert "~/.zshrc" in result.stdout
            assert "fpath" in result.stdout
            assert "compinit" in result.stdout

    def test_idempotent_reinstall(self) -> None:
        """Running init shell zsh twice succeeds and updates files."""
        with tempfile.TemporaryDirectory() as home:
            result1 = _run_init_shell("zsh", home)
            result2 = _run_init_shell("zsh", home)

            assert result1.returncode == 0
            assert result2.returncode == 0

            completion = Path(home) / ".zsh/completions/_dirq"
            wrapper = Path(home) / ".zsh/functions/dirq-wrapper"
            assert "#compdef dirq" in completion.read_text()
            assert "dirq()" in wrapper.read_text()


class TestInitShellErrors:
    """End-to-end error handling tests for init shell."""

    def test_unsupported_shell_produces_error(self) -> None:
        """dirq init shell nush produces error with supported shell list."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("nush", home)

            assert result.returncode == 2
            assert "error:" in result.stderr
            assert "invalid" in result.stderr.lower() or "unsupported" in result.stderr.lower()

    def test_unsupported_shell_creates_no_files(self) -> None:
        """Unsupported shell does not create any files."""
        with tempfile.TemporaryDirectory() as home:
            _run_init_shell("nush", home)

            # Home dir should still be empty
            entries = list(Path(home).iterdir())
            assert entries == []

    def test_exit_code_0_on_success(self) -> None:
        """Successful init shell returns exit code 0."""
        with tempfile.TemporaryDirectory() as home:
            for shell in ("fish", "bash", "zsh"):
                result = _run_init_shell(shell, home)
                assert result.returncode == 0, f"Failed for shell: {shell}"

    def test_exit_code_2_on_invalid_shell(self) -> None:
        """Invalid shell returns exit code 2."""
        with tempfile.TemporaryDirectory() as home:
            result = _run_init_shell("invalid", home)
            assert result.returncode == 2
