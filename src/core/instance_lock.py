"""
Single instance lock for Anti-Screensaver Mouse Mover

This module prevents multiple instances of the application from running
simultaneously using file-based locking via the fasteners library.
"""

import fasteners
from pathlib import Path
from typing import Optional
from .contracts import ISingleInstanceLock
from ..platform import get_lock_file_path


class FileLock(ISingleInstanceLock):
    """
    File-based single instance lock using fasteners.

    Uses a lock file in the temporary directory to prevent multiple
    instances. The lock is automatically released when the process exits.
    """

    def __init__(self, lock_path: Optional[Path] = None):
        """
        Initialize the instance lock.

        Args:
            lock_path: Optional custom lock file path (for testing)
        """
        self._lock_path = lock_path or get_lock_file_path()
        self._lock: Optional[fasteners.InterProcessLock] = None
        self._is_acquired = False

    def acquire(self) -> bool:
        """
        Attempt to acquire single instance lock.

        Returns:
            True if lock acquired successfully
            False if another instance is already running
        """
        if self._is_acquired:
            # Already acquired by this instance
            return True

        try:
            # Create lock object
            self._lock = fasteners.InterProcessLock(str(self._lock_path))

            # Try to acquire lock without blocking
            if self._lock.acquire(blocking=False):
                self._is_acquired = True
                return True
            else:
                # Lock is held by another process
                return False

        except Exception as e:
            # If we can't acquire the lock for any reason, assume another instance
            print(f"Error acquiring lock: {e}")
            return False

    def release(self) -> None:
        """
        Release the single instance lock.

        This is automatically called on process exit, but can be called
        manually for clean shutdown.
        """
        if self._lock and self._is_acquired:
            try:
                self._lock.release()
                self._is_acquired = False
            except Exception as e:
                print(f"Error releasing lock: {e}")

    def is_locked(self) -> bool:
        """
        Check if lock is currently held by this instance.

        Returns:
            True if this instance holds the lock, False otherwise
        """
        return self._is_acquired

    def __del__(self):
        """Ensure lock is released when object is destroyed."""
        self.release()

    def __enter__(self):
        """Context manager entry - acquire lock."""
        if not self.acquire():
            raise RuntimeError("Another instance is already running")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - release lock."""
        self.release()
        return False  # Don't suppress exceptions
