"""
Platform detection and path utilities for Windows

This module provides platform-specific path detection and configuration
for the Anti-Screensaver Mouse Mover application.
"""

import os
import platform
from pathlib import Path
from typing import Optional


def get_os_type() -> str:
    """
    Detect current operating system.

    Returns:
        "windows", "linux", or "macos"
    """
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    return system


def get_config_dir() -> Path:
    """
    Get platform-specific configuration directory.

    For Windows: %APPDATA%\AntiScreensaver
    For Linux: ~/.config/anti-screensaver
    For macOS: ~/Library/Application Support/AntiScreensaver

    Returns:
        Path object for configuration directory
    """
    os_type = get_os_type()

    if os_type == "windows":
        # Use APPDATA environment variable
        appdata = os.getenv("APPDATA")
        if not appdata:
            # Fallback to user profile
            userprofile = os.getenv("USERPROFILE", str(Path.home()))
            appdata = str(Path(userprofile) / "AppData" / "Roaming")
        return Path(appdata) / "AntiScreensaver"

    elif os_type == "linux":
        # Use XDG_CONFIG_HOME or fallback to ~/.config
        config_home = os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        return Path(config_home) / "anti-screensaver"

    else:  # macos
        return Path.home() / "Library" / "Application Support" / "AntiScreensaver"


def get_temp_dir() -> Path:
    """
    Get platform-specific temporary directory.

    For Windows: %TEMP%
    For Unix-like: /tmp

    Returns:
        Path object for temporary directory
    """
    return Path(os.getenv("TEMP", "/tmp"))


def ensure_config_dir() -> Path:
    """
    Ensure configuration directory exists.

    Returns:
        Path object for configuration directory

    Raises:
        OSError: If directory cannot be created
    """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_file_path() -> Path:
    """
    Get full path to configuration file.

    Returns:
        Path object for config.json file
    """
    return ensure_config_dir() / "config.json"


def get_lock_file_path() -> Path:
    """
    Get full path to single-instance lock file.

    Returns:
        Path object for lock file
    """
    return get_temp_dir() / "anti-screensaver.lock"


def get_log_file_path() -> Path:
    """
    Get full path to application log file.

    Returns:
        Path object for log file
    """
    return ensure_config_dir() / "anti-screensaver.log"


# Module-level constants
OS_TYPE = get_os_type()
CONFIG_DIR = get_config_dir()
CONFIG_FILE = get_config_file_path()
LOCK_FILE = get_lock_file_path()
LOG_FILE = get_log_file_path()
