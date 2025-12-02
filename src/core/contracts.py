"""
Interface contracts for Anti-Screensaver Mouse Mover

This module defines abstract base classes (ABCs) that establish contracts between
different layers and components of the application. These interfaces enable:
- Dependency injection for testability
- Platform-specific implementations
- Clear separation of concerns
"""

from abc import ABC, abstractmethod
from typing import Callable
from .models import Configuration, ApplicationState, MouseMovement


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
    def record_movement_failure(self, movement: MouseMovement) -> bool:
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
        """Release the single instance lock."""
        pass

    @abstractmethod
    def is_locked(self) -> bool:
        """
        Check if lock is currently held.

        Returns:
            True if locked (by this or another instance), False otherwise
        """
        pass
