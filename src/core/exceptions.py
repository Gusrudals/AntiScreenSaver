"""
Exception classes for Anti-Screensaver Mouse Mover

This module defines all custom exceptions used throughout the application.
All application-specific exceptions inherit from AntiScreensaverError.
"""


class AntiScreensaverError(Exception):
    """Base exception for all application errors."""
    pass


class ConfigurationError(AntiScreensaverError):
    """Configuration-related errors (load/save/validation failures)."""
    pass


class StateError(AntiScreensaverError):
    """State management errors (invalid transitions, inconsistent state)."""
    pass


class EngineError(AntiScreensaverError):
    """Movement engine errors (start/stop failures, timer issues)."""
    pass


class AutoStartError(AntiScreensaverError):
    """Auto-start configuration errors (registry access failures)."""
    pass


class InitializationError(AntiScreensaverError):
    """Application initialization errors (dependency failures, platform issues)."""
    pass


class ControllerError(AntiScreensaverError):
    """Application controller errors (coordination failures)."""
    pass
