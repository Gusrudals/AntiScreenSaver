"""
Windows-specific mouse control implementation

This module provides Windows mouse control using the pynput library.
It implements the IMouseController interface for dependency injection.
"""

from datetime import datetime
from typing import Optional
from pynput.mouse import Controller as PynputController
from ..core.contracts import IMouseController
from ..core.models import MouseMovement


class WindowsMouseController(IMouseController):
    """
    Windows mouse controller implementation using pynput.

    This class provides cross-platform mouse control that works on Windows
    without requiring special permissions or administrator rights.
    """

    def __init__(self):
        """Initialize the mouse controller."""
        self._controller = PynputController()
        self._last_error: Optional[str] = None

    def move(self, delta_x: int, delta_y: int) -> MouseMovement:
        """
        Move mouse cursor by specified pixel offset.

        Args:
            delta_x: Horizontal offset in pixels (positive = right)
            delta_y: Vertical offset in pixels (positive = down)

        Returns:
            MouseMovement object with execution result
        """
        timestamp = datetime.now()

        try:
            # Get current position for validation
            current_x, current_y = self._controller.position

            # Perform relative movement
            self._controller.move(delta_x, delta_y)

            # Verify movement occurred (optional, but good for diagnostics)
            new_x, new_y = self._controller.position

            success = True
            error_message = None
            self._last_error = None

        except Exception as e:
            success = False
            error_message = f"Mouse movement failed: {str(e)}"
            self._last_error = error_message

        return MouseMovement(
            delta_x=delta_x,
            delta_y=delta_y,
            timestamp=timestamp,
            success=success,
            error_message=error_message
        )

    def test_control(self) -> bool:
        """
        Test if mouse control is available on this system.

        Returns:
            True if mouse control is functional, False otherwise
        """
        try:
            # Try to get current position - if this works, control is available
            _ = self._controller.position
            return True
        except Exception as e:
            self._last_error = f"Mouse control test failed: {str(e)}"
            return False

    def get_current_position(self) -> tuple[int, int]:
        """
        Get current mouse cursor position (for diagnostics).

        Returns:
            Tuple of (x, y) screen coordinates
        """
        try:
            x, y = self._controller.position
            return (int(x), int(y))
        except Exception as e:
            self._last_error = f"Failed to get mouse position: {str(e)}"
            # Return a safe default
            return (0, 0)

    def get_last_error(self) -> Optional[str]:
        """
        Get the last error message (if any).

        Returns:
            Last error message or None
        """
        return self._last_error
