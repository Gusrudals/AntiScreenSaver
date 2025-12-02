"""
GUI components for Anti-Screensaver Mouse Mover

This package contains all UI-related code using PySide6 (Qt for Python).
"""

from .widgets import IntervalSlider
from .main_window import MainWindow
from .tray_icon import TrayIcon

__all__ = [
    'IntervalSlider',
    'MainWindow',
    'TrayIcon',
]
