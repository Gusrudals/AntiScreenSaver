"""
Data models for Anti-Screensaver Mouse Mover

This module defines all data classes and enumerations used throughout the application.
These are pure data structures with minimal behavior.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import re


class RunningState(Enum):
    """Application running state enumeration."""
    STOPPED = "stopped"
    RUNNING = "running"


class IconType(Enum):
    """System tray icon type enumeration."""
    IDLE = "idle"      # Gray icon when stopped
    ACTIVE = "active"  # Green icon when running


class OSType(Enum):
    """Operating system type enumeration."""
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"


@dataclass
class Configuration:
    """
    User configuration data class.

    Attributes:
        interval_seconds: Time between mouse movements (10-300 seconds)
        auto_start: Whether to start with Windows boot
        last_state: Last known running state (for UI consistency)
        version: Configuration schema version (semver format)
    """
    interval_seconds: int = 30
    auto_start: bool = False
    last_state: RunningState = RunningState.STOPPED
    version: str = "1.0.0"

    def validate(self) -> list[str]:
        """
        Validate configuration values.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate interval range
        if not (10 <= self.interval_seconds <= 300):
            errors.append(
                f"interval_seconds must be between 10 and 300, got {self.interval_seconds}"
            )

        # Validate auto_start type
        if not isinstance(self.auto_start, bool):
            errors.append(f"auto_start must be boolean, got {type(self.auto_start)}")

        # Validate last_state type
        if not isinstance(self.last_state, RunningState):
            errors.append(f"last_state must be RunningState enum, got {type(self.last_state)}")

        # Validate version format (semver)
        if not re.match(r'^\d+\.\d+\.\d+$', self.version):
            errors.append(f"version must match semver format (X.Y.Z), got {self.version}")

        return errors


@dataclass
class ApplicationState:
    """
    Runtime application state data class.

    Attributes:
        is_running: Whether mouse movement is actively running
        last_movement_timestamp: When the last successful movement occurred
        movement_count: Total movements since start (for diagnostics)
        error_count: Failed movement attempts (for reliability monitoring)
        start_timestamp: When the current session started
        instance_id: Unique identifier for this application instance
    """
    is_running: bool = False
    last_movement_timestamp: Optional[datetime] = None
    movement_count: int = 0
    error_count: int = 0
    start_timestamp: Optional[datetime] = None
    instance_id: str = ""

    def reset_counts(self) -> None:
        """Reset diagnostic counters when starting new session."""
        self.movement_count = 0
        self.error_count = 0


@dataclass
class MouseMovement:
    """
    Represents a single mouse movement operation.

    Attributes:
        delta_x: Horizontal movement in pixels (positive = right, negative = left)
        delta_y: Vertical movement in pixels (positive = down, negative = up)
        timestamp: When the movement was executed
        success: Whether the movement succeeded
        error_message: Error details if success=False
    """
    delta_x: int
    delta_y: int
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
