"""
Entry point for Anti-Screensaver Mouse Mover

This module provides the main entry point for the application.
It initializes the Qt application, parses command-line arguments,
and starts the application controller.
"""

import sys
import argparse

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from .controller import ApplicationController
from . import __version__


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed argument namespace
    """
    parser = argparse.ArgumentParser(
        prog="anti-screensaver",
        description="Prevent system idle/screensaver with periodic mouse movements"
    )

    parser.add_argument(
        "--minimized", "-m",
        action="store_true",
        help="Start minimized to system tray"
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    return parser.parse_args()


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Parse arguments
    args = parse_args()

    # Create Qt application
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Anti-Screensaver Mouse Mover")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("AntiScreensaver")

    # Don't quit when last window is closed (we have tray icon)
    app.setQuitOnLastWindowClosed(False)

    # Create and start controller
    controller = ApplicationController(start_minimized=args.minimized)

    if not controller.start():
        return 1

    # Run event loop
    exit_code = app.exec()

    # Cleanup
    controller.shutdown()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
