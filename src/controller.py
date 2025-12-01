"""
Application controller for Anti-Screensaver Mouse Mover

This module coordinates all components of the application including
GUI, movement engine, configuration, and state management.
"""

from datetime import datetime
from typing import Optional

from PySide6.QtCore import QObject, Slot, QTimer
from PySide6.QtWidgets import QApplication

from .core import (
    JsonConfigurationManager,
    InMemoryStateManager,
    MovementEngine,
    FileLock,
    Configuration,
    EngineError,
    ConfigurationError,
    ControllerError
)
from .platform.windows import WindowsMouseController
from .gui.main_window import MainWindow
from .gui.tray_icon import TrayIcon


class ApplicationController(QObject):
    """
    Main application controller.

    Responsibilities:
    - Initialize all components
    - Coordinate between GUI and core logic
    - Handle startup/shutdown
    - Manage configuration persistence
    """

    def __init__(self, start_minimized: bool = False):
        """
        Initialize the application controller.

        Args:
            start_minimized: Whether to start minimized to tray
        """
        super().__init__()

        self._start_minimized = start_minimized
        self._config: Optional[Configuration] = None

        # Initialize components
        self._init_components()
        self._connect_signals()
        self._load_configuration()

        # Setup diagnostic update timer
        self._diag_timer = QTimer()
        self._diag_timer.timeout.connect(self._update_diagnostics)
        self._diag_timer.start(1000)  # Update every second

    def _init_components(self):
        """Initialize all application components."""
        # Core components
        self._config_manager = JsonConfigurationManager()
        self._state_manager = InMemoryStateManager()
        self._mouse_controller = WindowsMouseController()
        self._instance_lock = FileLock()

        # Movement engine
        self._engine = MovementEngine(
            self._mouse_controller,
            self._state_manager
        )

        # GUI components
        self._main_window = MainWindow()
        self._tray_icon = TrayIcon()

    def _connect_signals(self):
        """Connect all signals between components."""
        # Main window signals
        self._main_window.start_requested.connect(self._on_start_requested)
        self._main_window.stop_requested.connect(self._on_stop_requested)
        self._main_window.interval_changed.connect(self._on_interval_changed)
        self._main_window.close_to_tray.connect(self._on_close_to_tray)

        # Tray icon signals
        self._tray_icon.start_requested.connect(self._on_start_requested)
        self._tray_icon.stop_requested.connect(self._on_stop_requested)
        self._tray_icon.show_window_requested.connect(self._on_show_window)
        self._tray_icon.exit_requested.connect(self._on_exit_requested)

        # Engine signals
        self._engine.movement_executed.connect(self._on_movement_executed)
        self._engine.movement_failed.connect(self._on_movement_failed)
        self._engine.auto_stopped.connect(self._on_auto_stopped)

        # State manager callbacks
        self._state_manager.subscribe_state_change(self._on_state_changed)

    def _load_configuration(self):
        """Load configuration from disk."""
        try:
            self._config = self._config_manager.load()

            # Apply to UI
            self._main_window.set_interval(self._config.interval_seconds)
            self._tray_icon.set_interval(self._config.interval_seconds)

        except ConfigurationError as e:
            # Use defaults and show warning
            self._config = self._config_manager.create_default()
            self._main_window.show_error(
                "Configuration Error",
                f"Could not load configuration: {e}\nUsing defaults."
            )

    def _save_configuration(self):
        """Save current configuration to disk."""
        if self._config:
            try:
                self._config_manager.save(self._config)
            except ConfigurationError as e:
                self._main_window.show_error(
                    "Save Error",
                    f"Could not save configuration: {e}"
                )

    def start(self) -> bool:
        """
        Start the application.

        Returns:
            True if started successfully, False otherwise
        """
        # Try to acquire instance lock
        if not self._instance_lock.acquire():
            self._main_window.show_error(
                "Already Running",
                "Another instance of Anti-Screensaver is already running."
            )
            return False

        # Test mouse control
        if not self._mouse_controller.test_control():
            self._main_window.show_error(
                "Mouse Control Error",
                "Unable to control mouse. Please check permissions."
            )
            return False

        # Show tray icon
        self._tray_icon.show()

        # Show main window or stay minimized
        if not self._start_minimized:
            self._main_window.show()

        return True

    def shutdown(self):
        """Perform graceful shutdown."""
        # Stop engine if running
        if self._engine.is_running():
            try:
                self._engine.stop()
            except EngineError:
                pass  # Ignore errors during shutdown

        # Save configuration
        self._save_configuration()

        # Release instance lock
        self._instance_lock.release()

        # Stop diagnostic timer
        self._diag_timer.stop()

    @Slot()
    def _on_start_requested(self):
        """Handle start request from GUI."""
        if self._engine.is_running():
            return

        interval = self._main_window.get_interval()

        try:
            self._engine.start(interval)
            self._tray_icon.show_started_notification()
        except EngineError as e:
            self._main_window.show_error("Start Error", str(e))
            self._tray_icon.show_error_notification(str(e))

    @Slot()
    def _on_stop_requested(self):
        """Handle stop request from GUI."""
        if not self._engine.is_running():
            return

        try:
            self._engine.stop()
            self._tray_icon.show_stopped_notification()
        except EngineError as e:
            self._main_window.show_error("Stop Error", str(e))

    @Slot(int)
    def _on_interval_changed(self, interval: int):
        """Handle interval change from GUI."""
        if self._config:
            self._config.interval_seconds = interval
            self._save_configuration()

        # Update tray tooltip
        self._tray_icon.set_interval(interval)

        # Update running engine if active
        if self._engine.is_running():
            try:
                self._engine.update_interval(interval)
            except EngineError as e:
                self._main_window.show_error("Interval Update Error", str(e))

    @Slot()
    def _on_close_to_tray(self):
        """Handle main window close (minimize to tray)."""
        # Window is already hidden by closeEvent
        self._tray_icon.show_message(
            "Anti-Screensaver",
            "Application minimized to tray. Click the tray icon to restore.",
        )

    @Slot()
    def _on_show_window(self):
        """Handle show window request from tray."""
        self._main_window.show()
        self._main_window.raise_()
        self._main_window.activateWindow()

    @Slot()
    def _on_exit_requested(self):
        """Handle exit request from tray."""
        self.shutdown()
        QApplication.quit()

    @Slot(int, int)
    def _on_movement_executed(self, delta_x: int, delta_y: int):
        """Handle successful movement."""
        state = self._state_manager.get_state()
        self._tray_icon.set_movement_count(state.movement_count)

    @Slot(str)
    def _on_movement_failed(self, error: str):
        """Handle failed movement."""
        # Only show error if multiple consecutive failures
        consecutive = self._state_manager.get_consecutive_errors()
        if consecutive >= 3:
            self._tray_icon.show_error_notification(
                f"Multiple movement failures ({consecutive}): {error}"
            )

    @Slot()
    def _on_auto_stopped(self):
        """Handle auto-stop due to error threshold."""
        self._main_window.show_error(
            "Auto-Stopped",
            "Mouse movement was stopped due to repeated failures.\n"
            "Please check your system permissions."
        )
        self._tray_icon.show_error_notification(
            "Auto-stopped due to repeated failures"
        )

    def _on_state_changed(self, is_running: bool):
        """Handle state change from state manager."""
        self._main_window.set_running_state(is_running)
        self._tray_icon.set_running_state(is_running)

    @Slot()
    def _update_diagnostics(self):
        """Update diagnostic display in main window."""
        state = self._state_manager.get_state()

        # Format last movement timestamp
        if state.last_movement_timestamp:
            last_str = state.last_movement_timestamp.strftime("%H:%M:%S")
        else:
            last_str = "Never"

        self._main_window.update_diagnostics(
            state.movement_count,
            state.error_count,
            last_str
        )
