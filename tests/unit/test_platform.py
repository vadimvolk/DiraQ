"""Tests for OS-specific config path resolution."""
import os
from pathlib import Path
from unittest import mock

from dirq.platform import get_config_path


class TestGetConfigPath:
    """Test OS-specific config path resolution."""

    def test_xdg_config_home_set_on_linux(self) -> None:
        """Use XDG_CONFIG_HOME when set on Linux."""
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/config"}):
            with mock.patch("platform.system", return_value="Linux"):
                result = get_config_path()
                assert result == Path("/custom/config/dirq/config.rc")

    def test_xdg_config_home_set_on_macos(self) -> None:
        """Use XDG_CONFIG_HOME when set on macOS."""
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/config"}):
            with mock.patch("platform.system", return_value="Darwin"):
                result = get_config_path()
                assert result == Path("/custom/config/dirq/config.rc")

    def test_xdg_config_home_set_on_windows(self) -> None:
        """Use XDG_CONFIG_HOME when set on Windows."""
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": "/custom/config"}):
            with mock.patch("platform.system", return_value="Windows"):
                result = get_config_path()
                assert result == Path("/custom/config/dirq/config.rc")

    def test_fallback_linux(self) -> None:
        """Fall back to ~/.config/dirq/config.rc on Linux when XDG not set."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("platform.system", return_value="Linux"):
                with mock.patch("pathlib.Path.home", return_value=Path("/home/user")):
                    result = get_config_path()
                    assert result == Path("/home/user/.config/dirq/config.rc")

    def test_fallback_macos(self) -> None:
        """Fall back to ~/Library/Application Support/dirq/config.rc on macOS when XDG not set."""
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("platform.system", return_value="Darwin"):
                with mock.patch("pathlib.Path.home", return_value=Path("/Users/user")):
                    result = get_config_path()
                    assert result == Path("/Users/user/Library/Application Support/dirq/config.rc")

    def test_fallback_windows(self) -> None:
        """Fall back to %APPDATA%\\dirq\\config.rc on Windows when XDG not set."""
        with mock.patch.dict(
            os.environ, {"APPDATA": "C:\\Users\\user\\AppData\\Roaming"}, clear=True
        ):
            with mock.patch("platform.system", return_value="Windows"):
                result = get_config_path()
                expected = Path("C:\\Users\\user\\AppData\\Roaming") / "dirq" / "config.rc"
                assert result == expected
