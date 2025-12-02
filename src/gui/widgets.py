"""
Reusable GUI widgets for Anti-Screensaver Mouse Mover

This module contains custom widgets used throughout the application.
"""

from PySide6.QtWidgets import QWidget, QSlider, QLabel, QHBoxLayout, QVBoxLayout, QSpinBox
from PySide6.QtCore import Qt, Signal


class IntervalSlider(QWidget):
    """
    Custom widget for configuring movement interval.

    Combines a slider with a spinbox for direct input and a label showing the current value.
    Range: 10-300 seconds
    """

    # Signal emitted when interval value changes
    interval_changed = Signal(int)

    def __init__(self, parent=None):
        """
        Initialize the interval slider widget.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Label row
        label_layout = QHBoxLayout()

        self._title_label = QLabel("Movement Interval:")
        label_layout.addWidget(self._title_label)

        label_layout.addStretch()

        self._value_label = QLabel("30 seconds")
        self._value_label.setMinimumWidth(80)
        label_layout.addWidget(self._value_label)

        layout.addLayout(label_layout)

        # Slider and spinbox row
        control_layout = QHBoxLayout()

        # Slider
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(10)
        self._slider.setMaximum(300)
        self._slider.setValue(30)
        self._slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider.setTickInterval(30)
        control_layout.addWidget(self._slider, stretch=1)

        # Spinbox for direct input
        self._spinbox = QSpinBox()
        self._spinbox.setMinimum(10)
        self._spinbox.setMaximum(300)
        self._spinbox.setValue(30)
        self._spinbox.setSuffix(" s")
        self._spinbox.setMinimumWidth(70)
        self._spinbox.setToolTip("Enter interval directly")
        control_layout.addWidget(self._spinbox)

        layout.addLayout(control_layout)

        # Range labels
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("10s"))
        range_layout.addStretch()
        range_layout.addWidget(QLabel("300s"))
        layout.addLayout(range_layout)

    def _connect_signals(self):
        """Connect internal signals."""
        self._slider.valueChanged.connect(self._on_slider_changed)
        self._spinbox.valueChanged.connect(self._on_spinbox_changed)

    def _on_slider_changed(self, value: int):
        """Handle slider value change."""
        # Block spinbox signals to avoid circular updates
        self._spinbox.blockSignals(True)
        self._spinbox.setValue(value)
        self._spinbox.blockSignals(False)

        self._update_value_label(value)
        self.interval_changed.emit(value)

    def _on_spinbox_changed(self, value: int):
        """Handle spinbox value change."""
        # Block slider signals to avoid circular updates
        self._slider.blockSignals(True)
        self._slider.setValue(value)
        self._slider.blockSignals(False)

        self._update_value_label(value)
        self.interval_changed.emit(value)

    def _update_value_label(self, value: int):
        """Update the value label text."""
        if value < 60:
            self._value_label.setText(f"{value} seconds")
        else:
            minutes = value // 60
            seconds = value % 60
            if seconds == 0:
                self._value_label.setText(f"{minutes} min")
            else:
                self._value_label.setText(f"{minutes}m {seconds}s")

    def get_value(self) -> int:
        """
        Get current interval value.

        Returns:
            Interval in seconds
        """
        return self._slider.value()

    def set_value(self, value: int):
        """
        Set interval value.

        Args:
            value: Interval in seconds (10-300)
        """
        # Clamp to valid range
        value = max(10, min(300, value))

        # Update both slider and spinbox
        self._slider.blockSignals(True)
        self._spinbox.blockSignals(True)

        self._slider.setValue(value)
        self._spinbox.setValue(value)
        self._update_value_label(value)

        self._slider.blockSignals(False)
        self._spinbox.blockSignals(False)

    def set_enabled(self, enabled: bool):
        """
        Enable or disable the slider and spinbox.

        Args:
            enabled: Whether the controls should be enabled
        """
        self._slider.setEnabled(enabled)
        self._spinbox.setEnabled(enabled)

    def is_warning_value(self) -> bool:
        """
        Check if current value is in warning range.

        Warning range: <15s or >180s

        Returns:
            True if value is extreme, False otherwise
        """
        value = self._slider.value()
        return value < 15 or value > 180
