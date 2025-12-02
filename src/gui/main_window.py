"""
Main window for Anti-Screensaver Mouse Mover

This module implements the main application window with start/stop controls,
interval configuration, and diagnostic information display.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QCloseEvent

from .widgets import IntervalSlider


class MainWindow(QMainWindow):
    """
    Main application window.

    Provides:
    - Start/Stop button for mouse movement control
    - Interval slider for configuration
    - Diagnostic information panel
    - Auto-start checkbox (future feature)
    - Minimize to tray on close
    """

    # Signals for controller communication
    start_requested = Signal()
    stop_requested = Signal()
    interval_changed = Signal(int)
    auto_start_changed = Signal(bool)
    click_enabled_changed = Signal(bool)
    close_to_tray = Signal()

    def __init__(self, parent=None):
        """
        Initialize the main window.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        self._is_running = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the window UI."""
        self.setWindowTitle("Anti-Screensaver Mouse Mover")
        self.setMinimumSize(400, 380)
        self.setMaximumSize(550, 500)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Status section
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self._status_label = QLabel("Stopped")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
                background-color: #f0f0f0;
                color: #666;
            }
        """)
        status_layout.addWidget(self._status_label)

        # Start/Stop button
        self._toggle_button = QPushButton("Start")
        self._toggle_button.setMinimumHeight(40)
        self._toggle_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        status_layout.addWidget(self._toggle_button)

        layout.addWidget(status_group)

        # Settings section
        settings_group = QGroupBox("Settings")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(10)

        # Interval slider
        self._interval_slider = IntervalSlider()
        settings_layout.addWidget(self._interval_slider)

        # Warning label for extreme values
        self._warning_label = QLabel("")
        self._warning_label.setStyleSheet("color: #ff9800; font-size: 11px;")
        self._warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._warning_label.hide()
        settings_layout.addWidget(self._warning_label)

        # Add some spacing before checkboxes
        settings_layout.addSpacing(5)

        # Auto-start checkbox (future feature placeholder)
        self._auto_start_checkbox = QCheckBox("Start with system (Windows only)")
        self._auto_start_checkbox.setEnabled(False)  # Disabled for now
        self._auto_start_checkbox.setToolTip("Auto-start feature coming soon")
        settings_layout.addWidget(self._auto_start_checkbox)

        # Click enabled checkbox
        self._click_enabled_checkbox = QCheckBox("Enable mouse click on movement")
        self._click_enabled_checkbox.setToolTip("Perform left mouse click when moving the mouse")
        settings_layout.addWidget(self._click_enabled_checkbox)

        layout.addWidget(settings_group)

        # Diagnostics section
        diag_group = QGroupBox("Diagnostics")
        diag_layout = QVBoxLayout(diag_group)
        diag_layout.setSpacing(8)

        diag_grid = QHBoxLayout()
        diag_grid.setSpacing(15)

        # Movement count
        count_layout = QVBoxLayout()
        count_layout.addWidget(QLabel("Movements:"))
        self._movement_count_label = QLabel("0")
        self._movement_count_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        count_layout.addWidget(self._movement_count_label)
        diag_grid.addLayout(count_layout)

        # Error count
        error_layout = QVBoxLayout()
        error_layout.addWidget(QLabel("Errors:"))
        self._error_count_label = QLabel("0")
        self._error_count_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        error_layout.addWidget(self._error_count_label)
        diag_grid.addLayout(error_layout)

        # Last movement
        last_layout = QVBoxLayout()
        last_layout.addWidget(QLabel("Last Movement:"))
        self._last_movement_label = QLabel("Never")
        self._last_movement_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        last_layout.addWidget(self._last_movement_label)
        diag_grid.addLayout(last_layout)

        diag_layout.addLayout(diag_grid)
        layout.addWidget(diag_group)

        # Stretch to push everything up
        layout.addStretch()

    def _connect_signals(self):
        """Connect internal signals."""
        self._toggle_button.clicked.connect(self._on_toggle_clicked)
        self._interval_slider.interval_changed.connect(self._on_interval_changed)
        self._auto_start_checkbox.stateChanged.connect(self._on_auto_start_changed)
        self._click_enabled_checkbox.stateChanged.connect(self._on_click_enabled_changed)

    def _on_toggle_clicked(self):
        """Handle start/stop button click."""
        if self._is_running:
            self.stop_requested.emit()
        else:
            self.start_requested.emit()

    def _on_interval_changed(self, value: int):
        """Handle interval slider change."""
        # Show/hide warning for extreme values
        if self._interval_slider.is_warning_value():
            if value < 15:
                self._warning_label.setText("Very short interval may increase CPU usage")
            else:
                self._warning_label.setText("Long interval may not prevent screen lock")
            self._warning_label.show()
        else:
            self._warning_label.hide()

        self.interval_changed.emit(value)

    def _on_auto_start_changed(self, state: int):
        """Handle auto-start checkbox change."""
        self.auto_start_changed.emit(state == Qt.CheckState.Checked.value)

    def _on_click_enabled_changed(self, state: int):
        """Handle click enabled checkbox change."""
        self.click_enabled_changed.emit(state == Qt.CheckState.Checked.value)

    @Slot(bool)
    def set_running_state(self, is_running: bool):
        """
        Update UI to reflect running state.

        Args:
            is_running: Whether the application is currently running
        """
        self._is_running = is_running

        if is_running:
            self._status_label.setText("Running")
            self._status_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #e8f5e9;
                    color: #2e7d32;
                }
            """)
            self._toggle_button.setText("Stop")
            self._toggle_button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
                QPushButton:pressed {
                    background-color: #b71c1c;
                }
            """)
        else:
            self._status_label.setText("Stopped")
            self._status_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    color: #666;
                }
            """)
            self._toggle_button.setText("Start")
            self._toggle_button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """)

    @Slot(int, int, str)
    def update_diagnostics(self, movement_count: int, error_count: int, last_movement: str):
        """
        Update diagnostic display.

        Args:
            movement_count: Total successful movements
            error_count: Total errors
            last_movement: Formatted timestamp of last movement
        """
        self._movement_count_label.setText(str(movement_count))
        self._error_count_label.setText(str(error_count))
        self._last_movement_label.setText(last_movement)

    def set_interval(self, interval_seconds: int):
        """
        Set the interval slider value.

        Args:
            interval_seconds: Interval in seconds
        """
        self._interval_slider.set_value(interval_seconds)

    def get_interval(self) -> int:
        """
        Get current interval value.

        Returns:
            Interval in seconds
        """
        return self._interval_slider.get_value()

    def set_auto_start(self, enabled: bool):
        """
        Set auto-start checkbox state.

        Args:
            enabled: Whether auto-start is enabled
        """
        self._auto_start_checkbox.setChecked(enabled)

    def set_click_enabled(self, enabled: bool):
        """
        Set click enabled checkbox state.

        Args:
            enabled: Whether click is enabled
        """
        self._click_enabled_checkbox.setChecked(enabled)

    def get_click_enabled(self) -> bool:
        """
        Get click enabled checkbox state.

        Returns:
            Whether click is enabled
        """
        return self._click_enabled_checkbox.isChecked()

    def show_error(self, title: str, message: str):
        """
        Show an error message box.

        Args:
            title: Message box title
            message: Error message
        """
        QMessageBox.critical(self, title, message)

    def show_info(self, title: str, message: str):
        """
        Show an information message box.

        Args:
            title: Message box title
            message: Info message
        """
        QMessageBox.information(self, title, message)

    def closeEvent(self, event: QCloseEvent):
        """
        Handle window close event.

        Instead of quitting, minimize to system tray.
        """
        event.ignore()
        self.hide()
        self.close_to_tray.emit()
