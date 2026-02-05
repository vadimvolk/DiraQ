"""OS-specific config path resolution."""
import os
import platform
from pathlib import Path


def get_config_path() -> Path:
    """
    Get the OS-specific config file path for dirq.

    Uses XDG_CONFIG_HOME if set, otherwise falls back to platform-specific defaults:
    - Linux: ~/.config/dirq/config.rc
    - macOS: ~/Library/Application Support/dirq/config.rc
    - Windows: %APPDATA%\\dirq\\config.rc

    Returns:
        Path to the config file.
    """
    # Check for XDG_CONFIG_HOME override
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "dirq" / "config.rc"

    # Platform-specific fallbacks
    system = platform.system()
    home = Path.home()

    if system == "Darwin":  # macOS
        return home / "Library" / "Application Support" / "dirq" / "config.rc"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", str(home / "AppData" / "Roaming"))
        return Path(appdata) / "dirq" / "config.rc"
    else:  # Linux and others
        return home / ".config" / "dirq" / "config.rc"
