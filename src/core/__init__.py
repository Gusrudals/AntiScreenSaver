"""
Core business logic for Anti-Screensaver Mouse Mover

This package contains the core functionality independent of GUI or platform.
"""

from .models import Configuration, ApplicationState, MouseMovement, RunningState, IconType
from .exceptions import (
    AntiScreensaverError,
    ConfigurationError,
    StateError,
    EngineError,
    AutoStartError,
    InitializationError,
    ControllerError
)
from .contracts import (
    IConfigurationManager,
    IMouseController,
    IStateManager,
    IMovementEngine,
    ISingleInstanceLock
)
from .config import JsonConfigurationManager
from .state import InMemoryStateManager
from .mouse_mover import MovementEngine
from .instance_lock import FileLock

__all__ = [
    # Models
    'Configuration',
    'ApplicationState',
    'MouseMovement',
    'RunningState',
    'IconType',
    # Exceptions
    'AntiScreensaverError',
    'ConfigurationError',
    'StateError',
    'EngineError',
    'AutoStartError',
    'InitializationError',
    'ControllerError',
    # Contracts
    'IConfigurationManager',
    'IMouseController',
    'IStateManager',
    'IMovementEngine',
    'ISingleInstanceLock',
    # Implementations
    'JsonConfigurationManager',
    'InMemoryStateManager',
    'MovementEngine',
    'FileLock',
]
