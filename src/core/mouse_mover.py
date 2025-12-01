"""
Mouse movement engine for Anti-Screensaver Mouse Mover

This module implements the core movement engine that executes periodic
micro mouse movements using Qt timers. It coordinates between the timer,
mouse controller, and state manager.
"""

from datetime import datetime
from PySide6.QtCore import QTimer, QObject, Signal
from typing import Optional
from .contracts import IMovementEngine, IMouseController, IStateManager
from .exceptions import EngineError


class MovementEngine(QObject, IMovementEngine):
    """
    Qt-based movement engine using QTimer.

    Uses alternating +1/-1 pixel pattern to keep mouse near original position
    while preventing system idle detection.

    Signals:
        movement_executed: Emitted after each successful movement (delta_x, delta_y)
        movement_failed: Emitted after failed movement (error_message)
        auto_stopped: Emitted when engine auto-stops due to error threshold
    """

    # Qt signals for event notifications
    movement_executed = Signal(int, int)  # delta_x, delta_y
    movement_failed = Signal(str)  # error_message
    auto_stopped = Signal()  # no parameters

    def __init__(
        self,
        mouse_controller: IMouseController,
        state_manager: IStateManager
    ):
        """
        Initialize movement engine.

        Args:
            mouse_controller: Controller for executing mouse movements
            state_manager: Manager for tracking application state
        """
        super().__init__()
        self._mouse_controller = mouse_controller
        self._state_manager = state_manager
        self._timer: Optional[QTimer] = None
        self._current_interval = 30  # Default 30 seconds
        self._pattern_state = 0  # 0 = move forward (+1,+1), 1 = move back (-1,-1)

    def start(self, interval_seconds: int) -> None:
        """
        Start periodic mouse movements.

        Args:
            interval_seconds: Time between movements in seconds

        Raises:
            EngineError: If already running or unable to start
        """
        if self.is_running():
            raise EngineError("Movement engine is already running")

        if interval_seconds < 10 or interval_seconds > 300:
            raise EngineError(f"Interval must be between 10 and 300 seconds, got {interval_seconds}")

        # Create and configure timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._execute_movement)
        self._current_interval = interval_seconds
        self._pattern_state = 0  # Reset pattern

        # Start timer (interval in milliseconds)
        self._timer.start(interval_seconds * 1000)

        # Update state manager
        try:
            self._state_manager.start()
        except Exception as e:
            self._timer.stop()
            self._timer = None
            raise EngineError(f"Failed to update state: {e}")

    def stop(self) -> None:
        """
        Stop periodic mouse movements.

        Raises:
            EngineError: If not running
        """
        if not self.is_running():
            raise EngineError("Movement engine is not running")

        # Stop timer
        if self._timer:
            self._timer.stop()
            self._timer = None

        # Update state manager
        try:
            self._state_manager.stop()
        except Exception as e:
            raise EngineError(f"Failed to update state: {e}")

    def is_running(self) -> bool:
        """
        Check if movement engine is currently active.

        Returns:
            True if running, False otherwise
        """
        return self._timer is not None and self._timer.isActive()

    def update_interval(self, interval_seconds: int) -> None:
        """
        Update movement interval while running.

        Args:
            interval_seconds: New interval in seconds

        Note:
            Change takes effect within 1 second (satisfies NFR-009)
        """
        if interval_seconds < 10 or interval_seconds > 300:
            raise EngineError(f"Interval must be between 10 and 300 seconds, got {interval_seconds}")

        self._current_interval = interval_seconds

        # If timer is active, restart it with new interval
        if self.is_running() and self._timer:
            self._timer.setInterval(interval_seconds * 1000)

    def get_next_movement_pattern(self) -> tuple[int, int]:
        """
        Get next movement deltas based on alternating pattern.

        Returns:
            Tuple of (delta_x, delta_y) for next movement

        Pattern:
            State 0: (+1, +1) - Move right and down
            State 1: (-1, -1) - Move left and up
            This returns cursor to approximately original position
        """
        if self._pattern_state == 0:
            return (1, 1)
        else:
            return (-1, -1)

    def _execute_movement(self) -> None:
        """
        Execute a single mouse movement (called by timer).

        This is the timer callback that performs the actual movement,
        handles errors, and updates state.
        """
        # Get movement pattern
        delta_x, delta_y = self.get_next_movement_pattern()

        # Execute movement
        movement = self._mouse_controller.move(delta_x, delta_y)

        if movement.success:
            # Record success
            self._state_manager.record_movement_success(movement)

            # Emit success signal
            self.movement_executed.emit(delta_x, delta_y)

            # Advance pattern state (0 -> 1 -> 0 -> 1 ...)
            self._pattern_state = 1 - self._pattern_state

        else:
            # Record failure
            should_auto_stop = self._state_manager.record_movement_failure(movement)

            # Emit failure signal
            error_msg = movement.error_message or "Unknown error"
            self.movement_failed.emit(error_msg)

            # Auto-stop if error threshold exceeded
            if should_auto_stop:
                try:
                    self.stop()
                    self.auto_stopped.emit()
                except Exception as e:
                    print(f"Error during auto-stop: {e}")

    def get_current_interval(self) -> int:
        """
        Get current movement interval.

        Returns:
            Interval in seconds
        """
        return self._current_interval
