"""
System tray icon for Anti-Screensaver Mouse Mover

This module implements the system tray icon with context menu
for controlling the application from the tray.
"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PySide6.QtCore import Signal, Slot, QSize


class TrayIcon(QSystemTrayIcon):
    """
    System tray icon with context menu.

    Provides:
    - Visual status indicator (green=running, gray=stopped)
    - Right-click menu with Start/Stop, Show Window, Exit
    - Click to show main window
    - Tooltip with status information
    """

    # Signals for controller communication
    start_requested = Signal()
    stop_requested = Signal()
    show_window_requested = Signal()
    exit_requested = Signal()

    def __init__(self, parent=None):
        """
        Initialize the tray icon.

        Args:
            parent: Parent object (optional)
        """
        super().__init__(parent)

        self._is_running = False
        self._interval = 30
        self._movement_count = 0

        self._setup_icons()
        self._setup_menu()
        self._connect_signals()

        # Set initial state
        self._update_icon()
        self._update_tooltip()

    def _setup_icons(self):
        """Create icons for different states."""
        # Create simple colored circle icons
        self._icon_stopped = self._create_circle_icon(QColor(128, 128, 128))  # Gray
        self._icon_running = self._create_circle_icon(QColor(76, 175, 80))    # Green

    def _create_circle_icon(self, color: QColor) -> QIcon:
        """
        Create a simple circle icon with the given color.

        Args:
            color: Fill color for the circle

        Returns:
            QIcon with the colored circle
        """
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(color)
        painter.setPen(QColor(0, 0, 0, 50))  # Slight border
        painter.drawEllipse(4, 4, size - 8, size - 8)
        painter.end()

        return QIcon(pixmap)

    def _setup_menu(self):
        """Set up the context menu."""
        self._menu = QMenu()

        # Start/Stop action
        self._toggle_action = QAction("Start", self)
        self._toggle_action.triggered.connect(self._on_toggle_clicked)
        self._menu.addAction(self._toggle_action)

        self._menu.addSeparator()

        # Show window action
        self._show_action = QAction("Show Window", self)
        self._show_action.triggered.connect(self.show_window_requested.emit)
        self._menu.addAction(self._show_action)

        self._menu.addSeparator()

        # Exit action
        self._exit_action = QAction("Exit", self)
        self._exit_action.triggered.connect(self.exit_requested.emit)
        self._menu.addAction(self._exit_action)

        self.setContextMenu(self._menu)

    def _connect_signals(self):
        """Connect internal signals."""
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        """
        Handle tray icon activation.

        Args:
            reason: How the icon was activated
        """
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click - show window
            self.show_window_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double click - also show window
            self.show_window_requested.emit()

    def _on_toggle_clicked(self):
        """Handle start/stop menu action click."""
        if self._is_running:
            self.stop_requested.emit()
        else:
            self.start_requested.emit()

    def _update_icon(self):
        """Update icon based on current state."""
        if self._is_running:
            self.setIcon(self._icon_running)
        else:
            self.setIcon(self._icon_stopped)

    def _update_tooltip(self):
        """Update tooltip with current status."""
        status = "Running" if self._is_running else "Stopped"
        tooltip = f"Anti-Screensaver Mouse Mover\n"
        tooltip += f"Status: {status}\n"
        tooltip += f"Interval: {self._interval}s"

        if self._is_running and self._movement_count > 0:
            tooltip += f"\nMovements: {self._movement_count}"

        self.setToolTip(tooltip)

    def _update_menu(self):
        """Update menu text based on current state."""
        if self._is_running:
            self._toggle_action.setText("Stop")
        else:
            self._toggle_action.setText("Start")

    @Slot(bool)
    def set_running_state(self, is_running: bool):
        """
        Update tray icon to reflect running state.

        Args:
            is_running: Whether the application is currently running
        """
        self._is_running = is_running
        self._update_icon()
        self._update_tooltip()
        self._update_menu()

    @Slot(int)
    def set_interval(self, interval_seconds: int):
        """
        Update displayed interval.

        Args:
            interval_seconds: Current interval setting
        """
        self._interval = interval_seconds
        self._update_tooltip()

    @Slot(int)
    def set_movement_count(self, count: int):
        """
        Update movement count display.

        Args:
            count: Total successful movements
        """
        self._movement_count = count
        self._update_tooltip()

    def show_message(self, title: str, message: str, icon_type=QSystemTrayIcon.MessageIcon.Information):
        """
        Show a system tray notification.

        Args:
            title: Notification title
            message: Notification message
            icon_type: Icon to show (Info, Warning, Critical)
        """
        if self.supportsMessages():
            self.showMessage(title, message, icon_type, 3000)

    def show_started_notification(self):
        """Show notification that mouse movement started."""
        self.show_message(
            "Anti-Screensaver",
            f"Mouse movement started (every {self._interval}s)",
            QSystemTrayIcon.MessageIcon.Information
        )

    def show_stopped_notification(self):
        """Show notification that mouse movement stopped."""
        self.show_message(
            "Anti-Screensaver",
            "Mouse movement stopped",
            QSystemTrayIcon.MessageIcon.Information
        )

    def show_error_notification(self, error: str):
        """
        Show error notification.

        Args:
            error: Error message
        """
        self.show_message(
            "Anti-Screensaver Error",
            error,
            QSystemTrayIcon.MessageIcon.Warning
        )
