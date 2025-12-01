# API Contracts

**Feature**: 001-anti-screensaver-mouse-mover
**Date**: 2024-12-01

## Overview

This directory contains the internal API contracts (interfaces) for the Anti-Screensaver Mouse Mover application. These are not REST or GraphQL APIs, but rather Python Abstract Base Classes (ABCs) that define the contracts between different layers and components of the application.

## Contract Files

### core_contracts.py

Defines all core component interfaces using Python ABCs. These interfaces establish the contracts between:

1. **Core Business Logic Layer**
   - `IConfigurationManager`: Configuration loading/saving
   - `IStateManager`: Application state management
   - `IMovementEngine`: Mouse movement execution engine
   - `IMouseController`: Platform-specific mouse control

2. **Platform Abstraction Layer**
   - `IPlatformInfo`: OS and display server detection
   - `IAutoStartManager`: Auto-start configuration
   - `ISingleInstanceLock`: Single instance enforcement

3. **GUI Layer**
   - `IMainWindow`: Main application window
   - `ITrayIcon`: System tray icon and menu

4. **Application Coordination Layer**
   - `IApplicationController`: Main controller coordinating all components

## Design Principles

### 1. Dependency Inversion

All components depend on abstractions (interfaces) rather than concrete implementations. This allows:
- Easy unit testing with mock implementations
- Platform-specific implementations swappable at runtime
- GUI framework independence (could replace PySide6 with another framework)

### 2. Single Responsibility

Each interface has a clear, focused responsibility:
- `IConfigurationManager` only handles config persistence
- `IMouseController` only handles mouse movements
- `IStateManager` only tracks runtime state

### 3. Interface Segregation

Interfaces are fine-grained. A component depending on `IMouseController` doesn't need to know about `IConfigurationManager`. This minimizes coupling.

### 4. Explicit Error Handling

Each interface documents which exceptions it may raise, enabling proper error handling at call sites.

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                  IApplicationController                          │
│  (Orchestrates all components, implements business logic)       │
└─────────────────┬──────────────┬──────────────┬─────────────────┘
                  │              │              │
        ┌─────────▼────┐  ┌──────▼──────┐  ┌───▼──────────┐
        │ IMainWindow  │  │ ITrayIcon   │  │ IMovementEngine│
        │              │  │             │  │                │
        └──────────────┘  └─────────────┘  └───┬────────────┘
                                                │
                  ┌─────────────────────────────┼─────────────┐
                  │                             │             │
         ┌────────▼─────────┐       ┌──────────▼──────┐  ┌───▼──────────┐
         │ IStateManager    │       │ IMouseController│  │ IConfiguration│
         │                  │       │                 │  │   Manager     │
         └──────────────────┘       └─────────────────┘  └───────────────┘
                                             │
                                    ┌────────▼────────┐
                                    │ IPlatformInfo   │
                                    │ IAutoStartMgr   │
                                    │ ISingleInstance │
                                    └─────────────────┘
```

## Implementation Guidelines

### For Implementers

1. **Create concrete classes** that inherit from these ABCs:
   ```python
   from contracts.core_contracts import IConfigurationManager, Configuration

   class JsonConfigurationManager(IConfigurationManager):
       def load(self) -> Configuration:
           # Implementation here
           pass

       def save(self, config: Configuration) -> None:
           # Implementation here
           pass

       # ... implement all abstract methods
   ```

2. **Use dependency injection** to provide implementations:
   ```python
   # Create implementations
   config_mgr = JsonConfigurationManager()
   state_mgr = InMemoryStateManager()
   mouse_ctrl = PynputMouseController()

   # Inject into controller
   controller = ApplicationController(
       config_manager=config_mgr,
       state_manager=state_mgr,
       mouse_controller=mouse_ctrl
   )
   ```

3. **Follow Liskov Substitution Principle**: Any implementation of an interface must be substitutable for any other implementation without breaking the application.

### For Test Writers

1. **Create mock implementations** for unit testing:
   ```python
   class MockMouseController(IMouseController):
       def __init__(self):
           self.movements = []

       def move(self, delta_x: int, delta_y: int) -> MouseMovement:
           movement = MouseMovement(
               delta_x=delta_x,
               delta_y=delta_y,
               timestamp=datetime.now(),
               success=True
           )
           self.movements.append(movement)
           return movement

       # ... other methods
   ```

2. **Test interactions** between components using real or mock implementations:
   ```python
   def test_movement_engine_calls_mouse_controller():
       mock_mouse = MockMouseController()
       engine = MovementEngine(mouse_controller=mock_mouse)

       engine.start(interval_seconds=1)
       time.sleep(1.5)
       engine.stop()

       assert len(mock_mouse.movements) >= 1
   ```

## Data Classes

The following data classes are defined in `core_contracts.py`:

- **Configuration**: User preferences (interval, auto-start, etc.)
- **ApplicationState**: Runtime state (running status, counters, timestamps)
- **MouseMovement**: Single movement operation result

These are concrete classes (not interfaces) as they are pure data with no behavior.

## Exception Hierarchy

```
AntiScreensaverError (base)
├── ConfigurationError
├── StateError
├── EngineError
├── AutoStartError
├── InitializationError
└── ControllerError
```

All application-specific exceptions inherit from `AntiScreensaverError`, allowing catch-all error handling when needed.

## Contract Versioning

Contracts should evolve carefully:

1. **Adding methods**: Add with default implementations or make optional
2. **Removing methods**: Deprecate first, remove in major version
3. **Changing signatures**: Avoid; add new method instead
4. **Breaking changes**: Only in major version bumps (2.0.0)

## Future Extensions

Potential future contracts (not in MVP):

- `ILoggingService`: Structured logging abstraction
- `IScheduler`: Time-based activation/deactivation
- `IExceptionProgramManager`: App-specific auto-pause rules
- `IUpdateChecker`: Application update notification
- `ITelemetryService`: Optional anonymous usage statistics (opt-in only)

## References

- **Feature Spec**: `../spec.md`
- **Data Model**: `../data-model.md`
- **Research**: `../research.md`

## Notes

These contracts are design artifacts. The actual implementation will be in the `src/` directory at the repository root. This contracts directory serves as the source of truth for component interfaces during implementation.
