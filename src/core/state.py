"""
State management for Anti-Screensaver Mouse Mover

This module tracks runtime application state including running status,
movement counters, and error tracking. It enforces state transition rules
and notifies listeners of state changes.
"""

import uuid
from datetime import datetime
from typing import Callable, List
from .contracts import IStateManager
from .models import ApplicationState, MouseMovement
from .exceptions import StateError


class InMemoryStateManager(IStateManager):
    """
    In-memory state manager implementation.

    Tracks runtime state, maintains diagnostic counters, and notifies
    subscribers of state changes. State is not persisted.
    """

    # Error threshold for auto-stop
    MAX_CONSECUTIVE_ERRORS = 5

    def __init__(self):
        """Initialize state manager with default stopped state."""
        self._state = ApplicationState(
            is_running=False,
            last_movement_timestamp=None,
            movement_count=0,
            error_count=0,
            start_timestamp=None,
            instance_id=str(uuid.uuid4())
        )
        self._subscribers: List[Callable[[bool], None]] = []
        self._consecutive_errors = 0  # Track consecutive errors for auto-stop

    def start(self) -> None:
        """
        Transition to running state.

        Raises:
            StateError: If already running
        """
        if self._state.is_running:
            raise StateError("Cannot start: already running")

        self._state.is_running = True
        self._state.start_timestamp = datetime.now()
        self._state.reset_counts()
        self._consecutive_errors = 0

        # Notify subscribers
        self._notify_state_change(True)

    def stop(self) -> None:
        """
        Transition to stopped state.

        Raises:
            StateError: If already stopped
        """
        if not self._state.is_running:
            raise StateError("Cannot stop: already stopped")

        self._state.is_running = False
        # Preserve counters for diagnostic display (don't reset)

        # Notify subscribers
        self._notify_state_change(False)

    def is_running(self) -> bool:
        """
        Check if application is currently running.

        Returns:
            True if running, False if stopped
        """
        return self._state.is_running

    def get_state(self) -> ApplicationState:
        """
        Get current application state snapshot.

        Returns:
            Copy of ApplicationState object with current values
        """
        # Return a copy to prevent external modification
        return ApplicationState(
            is_running=self._state.is_running,
            last_movement_timestamp=self._state.last_movement_timestamp,
            movement_count=self._state.movement_count,
            error_count=self._state.error_count,
            start_timestamp=self._state.start_timestamp,
            instance_id=self._state.instance_id
        )

    def record_movement_success(self, movement: MouseMovement) -> None:
        """
        Record successful mouse movement.

        Args:
            movement: MouseMovement that succeeded
        """
        self._state.movement_count += 1
        self._state.last_movement_timestamp = movement.timestamp
        self._consecutive_errors = 0  # Reset consecutive error counter

    def record_movement_failure(self, movement: MouseMovement) -> bool:
        """
        Record failed mouse movement attempt.

        Args:
            movement: MouseMovement that failed

        Returns:
            True if error threshold exceeded (should auto-stop), False otherwise
        """
        self._state.error_count += 1
        self._consecutive_errors += 1

        # Check if we've hit the error threshold
        if self._consecutive_errors >= self.MAX_CONSECUTIVE_ERRORS:
            return True  # Signal auto-stop needed
        return False

    def subscribe_state_change(self, callback: Callable[[bool], None]) -> None:
        """
        Subscribe to state change notifications.

        Args:
            callback: Function called with new running state (True/False)
        """
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe_state_change(self, callback: Callable[[bool], None]) -> None:
        """
        Unsubscribe from state change notifications.

        Args:
            callback: Function to remove from subscribers
        """
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def _notify_state_change(self, is_running: bool) -> None:
        """
        Notify all subscribers of state change.

        Args:
            is_running: New running state
        """
        for callback in self._subscribers:
            try:
                callback(is_running)
            except Exception as e:
                # Log error but don't let subscriber errors break state management
                print(f"Error in state change subscriber: {e}")

    def get_consecutive_errors(self) -> int:
        """
        Get count of consecutive errors.

        Returns:
            Number of consecutive errors
        """
        return self._consecutive_errors
