"""
Core Contracts: Anti-Screensaver Mouse Mover

This module defines the internal API contracts (interfaces) for core components.
These are not REST/GraphQL APIs but rather Python abstract base classes (ABCs)
that define the contracts between layers of the application.

Date: 2024-12-01
Status: Design specification (not implementation)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Callable


# ============================================================================
# Enums and Data Classes
# ============================================================================

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
    """User configuration data class."""
    interval_seconds: int  # Range: [10, 300]
    auto_start: bool
    last_state: RunningState
    version: str  # Semver format: X.Y.Z

    def validate(self) -> list[str]:
        """
        Validate configuration values.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        if not (10 <= self.interval_seconds <= 300):
            errors.append(f"interval_seconds must be between 10 and 300, got {self.interval_seconds}")
        if not isinstance(self.auto_start, bool):
            errors.append(f"auto_start must be boolean, got {type(self.auto_start)}")
        # Additional validation would be implemented here
        return errors


@dataclass
class ApplicationState:
    """Runtime application state data class."""
    is_running: bool
    last_movement_timestamp: Optional[datetime]
    movement_count: int
    error_count: int
    start_timestamp: Optional[datetime]
    instance_id: str

    def reset_counts(self) -> None:
        """Reset diagnostic counters when starting new session."""
        self.movement_count = 0
        self.error_count = 0


@dataclass
class MouseMovement:
    """Represents a single mouse movement operation."""
    delta_x: int
    delta_y: int
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None


# ============================================================================
# Core Component Interfaces
# ============================================================================

class IConfigurationManager(ABC):
    """
    Interface for configuration management.

    Responsibilities:
    - Load configuration from disk
    - Save configuration to disk
    - Validate configuration values
    - Provide defaults for missing values
    """

    @abstractmethod
    def load(self) -> Configuration:
        """
        Load configuration from disk.

        Returns:
            Configuration object with user settings

        Raises:
            ConfigurationError: If config is corrupted beyond recovery
        """
        pass

    @abstractmethod
    def save(self, config: Configuration) -> None:
        """
        Save configuration to disk.

        Args:
            config: Configuration object to persist

        Raises:
            ConfigurationError: If unable to write to disk
        """
        pass

    @abstractmethod
    def get_config_path(self) -> str:
        """
        Get platform-specific configuration file path.

        Returns:
            Absolute path to config file
        """
        pass

    @abstractmethod
    def create_default(self) -> Configuration:
        """
        Create default configuration.

        Returns:
            Configuration with default values
        """
        pass


class IMouseController(ABC):
    """
    Interface for mouse control operations.

    Responsibilities:
    - Execute mouse movements
    - Abstract platform-specific implementations
    - Report success/failure of movements
    """

    @abstractmethod
    def move(self, delta_x: int, delta_y: int) -> MouseMovement:
        """
        Move mouse cursor by specified pixel offset.

        Args:
            delta_x: Horizontal offset in pixels (positive = right)
            delta_y: Vertical offset in pixels (positive = down)

        Returns:
            MouseMovement object with execution result
        """
        pass

    @abstractmethod
    def test_control(self) -> bool:
        """
        Test if mouse control is available on this system.

        Returns:
            True if mouse control is functional, False otherwise
        """
        pass

    @abstractmethod
    def get_current_position(self) -> tuple[int, int]:
        """
        Get current mouse cursor position (for diagnostics).

        Returns:
            Tuple of (x, y) screen coordinates
        """
        pass


class IStateManager(ABC):
    """
    Interface for application state management.

    Responsibilities:
    - Track runtime state (running/stopped)
    - Maintain diagnostic counters
    - Enforce state transition rules
    - Notify listeners of state changes
    """

    @abstractmethod
    def start(self) -> None:
        """
        Transition to running state.

        Raises:
            StateError: If already running or in invalid state
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Transition to stopped state.

        Raises:
            StateError: If already stopped
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if application is currently running.

        Returns:
            True if running, False if stopped
        """
        pass

    @abstractmethod
    def get_state(self) -> ApplicationState:
        """
        Get current application state snapshot.

        Returns:
            ApplicationState object with current values
        """
        pass

    @abstractmethod
    def record_movement_success(self, movement: MouseMovement) -> None:
        """
        Record successful mouse movement.

        Args:
            movement: MouseMovement that succeeded
        """
        pass

    @abstractmethod
    def record_movement_failure(self, movement: MouseMovement) -> None:
        """
        Record failed mouse movement attempt.

        Args:
            movement: MouseMovement that failed

        Returns:
            True if error threshold exceeded (should auto-stop)
        """
        pass

    @abstractmethod
    def subscribe_state_change(self, callback: Callable[[bool], None]) -> None:
        """
        Subscribe to state change notifications.

        Args:
            callback: Function called with new running state (True/False)
        """
        pass


class IMovementEngine(ABC):
    """
    Interface for mouse movement engine.

    Responsibilities:
    - Execute periodic mouse movements
    - Manage movement patterns
    - Coordinate between timer and mouse controller
    """

    @abstractmethod
    def start(self, interval_seconds: int) -> None:
        """
        Start periodic mouse movements.

        Args:
            interval_seconds: Time between movements in seconds

        Raises:
            EngineError: If already running or unable to start
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stop periodic mouse movements.

        Raises:
            EngineError: If not running
        """
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if movement engine is currently active.

        Returns:
            True if running, False otherwise
        """
        pass

    @abstractmethod
    def update_interval(self, interval_seconds: int) -> None:
        """
        Update movement interval while running.

        Args:
            interval_seconds: New interval in seconds

        Note:
            Change must take effect within 1 second (NFR-009)
        """
        pass

    @abstractmethod
    def get_next_movement_pattern(self) -> tuple[int, int]:
        """
        Get next movement deltas based on pattern.

        Returns:
            Tuple of (delta_x, delta_y) for next movement
        """
        pass


# ============================================================================
# Platform Abstraction Interfaces
# ============================================================================

class IPlatformInfo(ABC):
    """
    Interface for platform-specific information.

    Responsibilities:
    - Detect operating system
    - Detect display server (Linux)
    - Provide platform-specific paths
    """

    @abstractmethod
    def get_os_type(self) -> OSType:
        """
        Detect current operating system.

        Returns:
            OSType enum value
        """
        pass

    @abstractmethod
    def get_display_server(self) -> Optional[str]:
        """
        Get display server type (Linux only).

        Returns:
            "x11", "wayland", or None if not Linux/not detected
        """
        pass

    @abstractmethod
    def get_autostart_path(self) -> str:
        """
        Get platform-specific autostart file/registry path.

        Returns:
            Absolute path or registry key string
        """
        pass

    @abstractmethod
    def get_config_dir(self) -> str:
        """
        Get platform-specific configuration directory.

        Returns:
            Absolute path to config directory
        """
        pass


class IAutoStartManager(ABC):
    """
    Interface for auto-start functionality.

    Responsibilities:
    - Enable/disable auto-start on system boot
    - Check current auto-start status
    - Handle platform-specific implementations
    """

    @abstractmethod
    def enable(self) -> None:
        """
        Enable auto-start on system boot.

        Raises:
            AutoStartError: If unable to configure auto-start
        """
        pass

    @abstractmethod
    def disable(self) -> None:
        """
        Disable auto-start on system boot.

        Raises:
            AutoStartError: If unable to modify auto-start
        """
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        """
        Check if auto-start is currently enabled.

        Returns:
            True if enabled, False otherwise
        """
        pass


class ISingleInstanceLock(ABC):
    """
    Interface for single instance enforcement.

    Responsibilities:
    - Acquire lock to prevent multiple instances
    - Release lock on application exit
    - Check if another instance is running
    """

    @abstractmethod
    def acquire(self) -> bool:
        """
        Attempt to acquire single instance lock.

        Returns:
            True if lock acquired, False if another instance running
        """
        pass

    @abstractmethod
    def release(self) -> None:
        """
        Release the single instance lock.
        """
        pass

    @abstractmethod
    def is_locked(self) -> bool:
        """
        Check if lock is currently held.

        Returns:
            True if locked (by this or another instance), False otherwise
        """
        pass


# ============================================================================
# GUI Component Interfaces
# ============================================================================

class IMainWindow(ABC):
    """
    Interface for main application window.

    Responsibilities:
    - Display start/stop controls
    - Show interval configuration slider
    - Display diagnostic information
    - Minimize to tray when started
    """

    @abstractmethod
    def show(self) -> None:
        """Display the main window."""
        pass

    @abstractmethod
    def hide(self) -> None:
        """Hide the main window (minimize to tray)."""
        pass

    @abstractmethod
    def update_state_display(self, state: ApplicationState) -> None:
        """
        Update UI to reflect current application state.

        Args:
            state: Current application state
        """
        pass

    @abstractmethod
    def update_config_display(self, config: Configuration) -> None:
        """
        Update UI to reflect current configuration.

        Args:
            config: Current configuration
        """
        pass

    @abstractmethod
    def set_start_callback(self, callback: Callable[[], None]) -> None:
        """
        Set callback for start button click.

        Args:
            callback: Function to call when user clicks start
        """
        pass

    @abstractmethod
    def set_stop_callback(self, callback: Callable[[], None]) -> None:
        """
        Set callback for stop button click.

        Args:
            callback: Function to call when user clicks stop
        """
        pass

    @abstractmethod
    def set_interval_change_callback(self, callback: Callable[[int], None]) -> None:
        """
        Set callback for interval slider change.

        Args:
            callback: Function to call with new interval value
        """
        pass


class ITrayIcon(ABC):
    """
    Interface for system tray icon.

    Responsibilities:
    - Display icon with status indicator
    - Provide context menu
    - Handle tray icon clicks
    """

    @abstractmethod
    def show(self) -> None:
        """Display the tray icon."""
        pass

    @abstractmethod
    def hide(self) -> None:
        """Hide the tray icon."""
        pass

    @abstractmethod
    def update_icon(self, icon_type: IconType) -> None:
        """
        Update tray icon appearance.

        Args:
            icon_type: IDLE or ACTIVE icon type
        """
        pass

    @abstractmethod
    def update_tooltip(self, text: str) -> None:
        """
        Update tray icon tooltip text.

        Args:
            text: Tooltip text to display on hover
        """
        pass

    @abstractmethod
    def set_toggle_callback(self, callback: Callable[[], None]) -> None:
        """
        Set callback for toggle running/stopped action.

        Args:
            callback: Function to call when user toggles state
        """
        pass

    @abstractmethod
    def set_show_window_callback(self, callback: Callable[[], None]) -> None:
        """
        Set callback for showing main window.

        Args:
            callback: Function to call when user wants to show window
        """
        pass

    @abstractmethod
    def set_exit_callback(self, callback: Callable[[], None]) -> None:
        """
        Set callback for application exit.

        Args:
            callback: Function to call when user selects exit
        """
        pass


# ============================================================================
# Application Controller Interface
# ============================================================================

class IApplicationController(ABC):
    """
    Interface for main application controller.

    Responsibilities:
    - Coordinate between all components
    - Handle application lifecycle
    - Implement business logic
    - React to user actions
    """

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize application components.

        Raises:
            InitializationError: If initialization fails
        """
        pass

    @abstractmethod
    def start_movement(self) -> None:
        """
        Start mouse movement engine.

        Raises:
            ControllerError: If unable to start
        """
        pass

    @abstractmethod
    def stop_movement(self) -> None:
        """
        Stop mouse movement engine.

        Raises:
            ControllerError: If unable to stop
        """
        pass

    @abstractmethod
    def update_interval(self, interval_seconds: int) -> None:
        """
        Update movement interval and save to config.

        Args:
            interval_seconds: New interval value
        """
        pass

    @abstractmethod
    def toggle_auto_start(self, enabled: bool) -> None:
        """
        Enable or disable auto-start.

        Args:
            enabled: True to enable, False to disable
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        Shutdown application cleanly.
        """
        pass


# ============================================================================
# Exception Classes
# ============================================================================

class AntiScreensaverError(Exception):
    """Base exception for all application errors."""
    pass


class ConfigurationError(AntiScreensaverError):
    """Configuration-related errors."""
    pass


class StateError(AntiScreensaverError):
    """State management errors."""
    pass


class EngineError(AntiScreensaverError):
    """Movement engine errors."""
    pass


class AutoStartError(AntiScreensaverError):
    """Auto-start configuration errors."""
    pass


class InitializationError(AntiScreensaverError):
    """Application initialization errors."""
    pass


class ControllerError(AntiScreensaverError):
    """Application controller errors."""
    pass
