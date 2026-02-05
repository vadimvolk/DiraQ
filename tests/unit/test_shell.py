"""Tests for shell script generation."""
import pytest


class TestShellScriptGeneration:
    """Test shell script generation for different shells."""

    def test_fish_output_contains_function(self) -> None:
        """Fish output contains function named dirq wrapping dirq navigate with cd."""
        from dirq.shell import generate_shell_script

        script = generate_shell_script("fish")

        assert "function dirq" in script
        assert "dirq navigate" in script or "command dirq navigate" in script
        assert "cd" in script

    def test_fish_output_contains_completions(self) -> None:
        """Fish output contains static completion definitions."""
        from dirq.shell import generate_shell_script

        script = generate_shell_script("fish")

        # Should have completions for subcommands
        assert "complete" in script
        # Should mention subcommands
        assert "navigate" in script or "save" in script

    def test_bash_output_contains_function(self) -> None:
        """Bash output contains function named dirq with cd."""
        from dirq.shell import generate_shell_script

        script = generate_shell_script("bash")

        assert "dirq()" in script or "function dirq" in script
        assert "cd" in script

    def test_bash_output_contains_completions(self) -> None:
        """Bash output contains static completion setup."""
        from dirq.shell import generate_shell_script

        script = generate_shell_script("bash")

        # Should have completion setup
        assert "complete" in script

    def test_zsh_output_contains_function(self) -> None:
        """Zsh output contains function named dirq with cd."""
        from dirq.shell import generate_shell_script

        script = generate_shell_script("zsh")

        assert "dirq()" in script or "function dirq" in script
        assert "cd" in script

    def test_zsh_output_contains_completions(self) -> None:
        """Zsh output contains static completion setup."""
        from dirq.shell import generate_shell_script

        script = generate_shell_script("zsh")

        # Should have completion setup
        assert "compdef" in script or "#compdef" in script

    def test_unsupported_shell_raises_error(self) -> None:
        """Unsupported shell type raises error listing supported shells."""
        from dirq.shell import generate_shell_script

        with pytest.raises(ValueError, match="unsupported shell"):
            generate_shell_script("nush")

        with pytest.raises(ValueError, match="fish.*bash.*zsh"):
            generate_shell_script("powershell")
