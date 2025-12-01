# Data Model: Anti-Screensaver Mouse Mover

**Feature**: 001-anti-screensaver-mouse-mover
**Date**: 2024-12-01
**Status**: Complete

## Overview

This document defines all entities, their attributes, relationships, validation rules, and state transitions for the Anti-Screensaver Mouse Mover application. The data model is intentionally simple to maintain low complexity and meet performance requirements.

---

## Core Entities

### 1. Configuration

**Purpose**: Stores user preferences and application settings. Persisted to disk as JSON.

**Attributes**:

| Attribute | Type | Required | Default | Validation Rules |
|-----------|------|----------|---------|------------------|
| `interval_seconds` | integer | Yes | 30 | Min: 10, Max: 300 (5 minutes) |
| `auto_start` | boolean | Yes | false | true or false |
| `last_state` | string | Yes | "stopped" | Enum: ["running", "stopped"] |
| `version` | string | Yes | "1.0.0" | Semantic version format (X.Y.Z) |
| `config_path` | string | No | (runtime) | Read-only, platform-specific |

**Validation Rules**:
- `interval_seconds` must be divisible by 1 (integer seconds only)
- If `interval_seconds < 10`, display warning about potential detection
- If `interval_seconds > 300`, display warning about potential lock screen activation
- `version` must match semver pattern: `\d+\.\d+\.\d+`
- `last_state` persists state across restarts for UI consistency (not functional state)

**Example JSON**:
```json
{
  "interval_seconds": 30,
  "auto_start": false,
  "last_state": "stopped",
  "version": "1.0.0"
}
```

**Storage Location**:
- Linux: `~/.config/anti-screensaver/config.json`
- Windows: `%APPDATA%\AntiScreensaver\config.json` (future)
- macOS: `~/Library/Application Support/AntiScreensaver/config.json` (future)

---

### 2. ApplicationState

**Purpose**: Tracks runtime state of the application. Not persisted (in-memory only).

**Attributes**:

| Attribute | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `is_running` | boolean | Yes | false | Whether mouse movement is actively running |
| `last_movement_timestamp` | datetime | No | None | Last successful mouse movement (ISO 8601) |
| `movement_count` | integer | Yes | 0 | Total movements since start (for diagnostics) |
| `error_count` | integer | Yes | 0 | Failed movement attempts (for reliability monitoring) |
| `start_timestamp` | datetime | No | None | When current session started |
| `instance_id` | string | Yes | (UUID) | Unique ID for this application instance |

**State Transitions**:

```
[Stopped] --start()--> [Running]
   ^                        |
   |                        |
   +------stop()------------+
```

**Transition Rules**:
- `start()`: Sets `is_running=true`, records `start_timestamp`, resets `movement_count=0`
- `stop()`: Sets `is_running=false`, preserves counts for diagnostic display
- On successful movement: Increment `movement_count`, update `last_movement_timestamp`
- On failed movement: Increment `error_count`, log error

**Error Threshold**:
- If `error_count >= 5` consecutive failures: Notify user, auto-stop timer
- Display warning: "Mouse control failed. Check permissions."

---

### 3. MouseMovement

**Purpose**: Encapsulates a single mouse movement operation. Ephemeral entity (not stored).

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `delta_x` | integer | Yes | Horizontal movement in pixels (can be negative) |
| `delta_y` | integer | Yes | Vertical movement in pixels (can be negative) |
| `timestamp` | datetime | Yes | When movement executed (ISO 8601) |
| `success` | boolean | Yes | Whether movement succeeded |
| `error_message` | string | No | Error details if `success=false` |

**Movement Pattern** (Default Strategy):
Alternating pattern to return cursor to approximate starting position:
1. Move `(+1, +1)` - right and down
2. Wait `interval_seconds`
3. Move `(-1, -1)` - left and up
4. Wait `interval_seconds`
5. Repeat

**Rationale**: Micro-movements are imperceptible and cursor roughly returns to origin, minimizing user interference.

**Alternative Patterns** (Future Enhancement):
- Circular pattern (8 points on circle)
- Random direction (noise pattern)
- User-configurable pattern

---

### 4. TrayIconState

**Purpose**: Manages system tray icon appearance and menu. Not persisted.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `icon_type` | string | Yes | Enum: ["idle", "active"] - determines icon image |
| `tooltip_text` | string | Yes | Hover text (e.g., "Running - 30s interval") |
| `menu_items` | list | Yes | Menu options with enabled states |

**Icon Types**:
- **Idle**: Gray icon, tooltip: "Anti-Screensaver (Stopped)"
- **Active**: Green icon, tooltip: "Anti-Screensaver (Running - {interval}s)"

**Menu Structure**:
```
Anti-Screensaver Mouse Mover
├── [✓] Running / [  ] Stopped (toggle)
├── Settings...
├── About
├── ---
└── Exit
```

**Menu State Logic**:
- If `ApplicationState.is_running == true`: Show "Running ✓"
- If `ApplicationState.is_running == false`: Show "Stopped"
- Click to toggle state (call `start()` or `stop()`)

---

### 5. PlatformInfo

**Purpose**: Abstracts platform-specific details. Detected at runtime.

**Attributes**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `os_type` | string | Yes | Enum: ["linux", "windows", "macos"] |
| `display_server` | string | No | For Linux: ["x11", "wayland", "unknown"] |
| `mouse_controller` | object | Yes | Platform-specific mouse control instance |
| `autostart_path` | string | Yes | Path to autostart file/registry key |

**Platform Detection**:
```python
import platform
import os

os_type = platform.system().lower()  # "linux", "windows", "darwin"
display_server = os.environ.get('XDG_SESSION_TYPE', 'unknown')  # Linux only
```

**Autostart Paths**:
- Linux: `~/.config/autostart/anti-screensaver.desktop`
- Windows: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- macOS: `~/Library/LaunchAgents/com.antiscreensaver.plist`

---

## Entity Relationships

```
Configuration (1) --loads--> ApplicationState (1)
       |                           |
       |                           v
       |                    MouseMovement (*)
       |                           ^
       |                           |
       +--configures--> Timer (1) -+

ApplicationState (1) --updates--> TrayIconState (1)

PlatformInfo (1) --provides--> MouseController (1)
                                      |
                                      +--executes--> MouseMovement (*)
```

**Relationship Descriptions**:
- **Configuration → ApplicationState**: Configuration is loaded once at startup to initialize state
- **Configuration → Timer**: Interval from config determines timer frequency
- **Timer → MouseMovement**: Each timer tick creates a new MouseMovement operation
- **ApplicationState → TrayIconState**: State changes trigger tray icon updates
- **PlatformInfo → MouseController**: Platform detection determines which controller implementation to use
- **MouseController → MouseMovement**: Controller executes movements and reports success/failure

---

## Validation Rules Summary

### Configuration Validation

**On Load**:
1. Validate JSON schema (required fields present, correct types)
2. Check `interval_seconds` range [10, 300]
3. Validate `version` matches semver pattern
4. Check `last_state` is valid enum value
5. Coerce `auto_start` to boolean if string ("true" → true)

**On Save**:
1. Ensure all required fields present
2. Format JSON with indentation (pretty-print) for human readability
3. Write atomically (write to temp file, then rename) to prevent corruption

**Error Handling**:
- If config file missing: Create with defaults
- If config file corrupted: Backup to `.config.json.bak`, create new defaults
- If config unwritable: Log warning, continue with in-memory config (changes not persisted)

---

### Runtime State Validation

**Movement Execution Validation**:
1. Check `is_running` before each movement attempt
2. Verify timer not already running when starting
3. Validate mouse controller initialized successfully
4. Catch exceptions during mouse movement and record in `error_count`

**Startup Validation**:
1. Verify single instance (check lock file)
2. Validate platform supported (OS detection)
3. Test mouse controller can perform test movement
4. Verify config directory writable

---

## State Machine Diagram

### Application Lifecycle States

```
┌─────────────┐
│  Initializing│
└──────┬──────┘
       │
       v
┌─────────────┐      user clicks     ┌─────────────┐
│   Stopped   │────── "Start" ──────>│   Running   │
│             │                       │             │
│ Timer: Off  │<───── "Stop" ────────│ Timer: On   │
│ Icon: Gray  │      user clicks     │ Icon: Green │
└──────┬──────┘                       └──────┬──────┘
       │                                     │
       │                                     │ timer tick
       │                                     v
       │                              ┌─────────────┐
       │                              │   Moving    │
       │                              │             │
       │                              │ Execute     │
       │<─────────────────────────────│ Movement    │
       │        on error (5x)         └──────┬──────┘
       │                                     │
       │                                     v
       │                              (return to Running)
       │
       v
┌─────────────┐
│   Exiting   │
└─────────────┘
```

**State Descriptions**:

1. **Initializing**: Load config, detect platform, initialize GUI
   - Duration: <2 seconds (NFR-008)
   - Transitions to: **Stopped**

2. **Stopped**: Idle state, timer not running, icon gray
   - Transitions to: **Running** (user action) or **Exiting** (user quits)

3. **Running**: Timer active, mouse movements occurring periodically
   - Transitions to: **Moving** (timer tick) or **Stopped** (user action/error threshold)

4. **Moving**: Executing mouse movement operation
   - Duration: <10ms typically
   - Transitions to: **Running** (success or single error) or **Stopped** (5+ consecutive errors)

5. **Exiting**: Cleanup (save config, release lock, stop timer)
   - Duration: <1 second
   - Transitions to: (process ends)

---

## Data Access Patterns

### Configuration Access

**Read Operations**:
- **Startup**: Read once, load into memory
- **Settings Dialog Open**: Display current values from memory
- **Frequency**: Once at startup, rarely during runtime

**Write Operations**:
- **User Changes Settings**: Immediate write to disk + update in-memory
- **App Shutdown**: Write `last_state` to preserve UI consistency
- **Auto-start Toggle**: Update config + modify autostart file/registry
- **Frequency**: Only on user action (infrequent)

**Concurrency**: None expected (single-threaded Qt event loop)

---

### State Access

**Read Operations**:
- **UI Updates**: Check `is_running` to update button text, icon
- **Timer Callback**: Check `is_running` before movement (safety check)
- **Status Display**: Read `movement_count`, `last_movement_timestamp` for diagnostics
- **Frequency**: High (every UI update, every timer tick)

**Write Operations**:
- **Start/Stop Actions**: Toggle `is_running`
- **Movement Success**: Update `last_movement_timestamp`, increment `movement_count`
- **Movement Failure**: Increment `error_count`
- **Frequency**: High (every movement attempt)

**Concurrency**: Single-threaded (Qt signals ensure serialization)

---

## Migration Strategy

### Configuration Version Migrations

**Current Version**: 1.0.0

**Future Migration Example** (1.0.0 → 1.1.0):
```python
def migrate_config(config: dict) -> dict:
    version = config.get('version', '1.0.0')

    if version == '1.0.0':
        # Add new field in 1.1.0
        config['movement_pattern'] = 'alternating'
        config['version'] = '1.1.0'

    return config
```

**Migration Rules**:
- Always preserve existing fields
- Add new fields with sensible defaults
- Never remove fields (deprecate instead)
- Log migration actions for troubleshooting

---

## Privacy and Security Considerations

### Data Privacy

**No Collection**: This application explicitly does NOT collect:
- User activity logs
- Mouse movement history (beyond last timestamp)
- System information beyond platform detection
- Network requests or telemetry

**Local-Only Storage**: All data stored locally in user's home directory

**Sensitive Data**: None. Configuration contains only:
- Numeric interval (not sensitive)
- Boolean flags (not sensitive)
- No passwords, API keys, or personal information

### Security Considerations

**Input Validation**: All user inputs validated:
- Interval slider bounds enforced at UI and config level
- File paths sanitized before writing

**File Permissions**:
- Config file: User read/write only (`chmod 600` equivalent)
- Lock file: User read/write only
- Log file: User read/write only

**No Privilege Escalation**: Application runs with user privileges, never requests root/admin

---

## Performance Implications

### Memory Footprint

**Estimated Memory Usage**:
- Python interpreter: ~15-20 MB
- PySide6 GUI: ~20-30 MB
- Application code + data: ~5 MB
- **Total**: ~40-55 MB (within <50MB requirement)

**Data Structure Sizes**:
- Configuration object: ~200 bytes
- ApplicationState object: ~500 bytes
- MouseMovement (ephemeral): ~150 bytes each (immediately discarded)

### CPU Usage

**Timer Overhead**: QTimer internal mechanism ~0.01% CPU
**Movement Execution**: Mouse control ~0.05% CPU per movement
**Idle CPU**: ~0.1% (GUI event loop overhead)
**Peak CPU**: ~0.5% during movement (well under 1% requirement)

### Disk I/O

**Configuration Writes**: ~1 KB per write (infrequent)
**Log Writes**: ~100 bytes per movement (if DEBUG enabled; INFO level: minimal)
**Autostart File**: ~200 bytes (one-time write)

**I/O Frequency**:
- Config: <10 writes per session (user actions only)
- Logs: Batched by logging framework (minimal overhead)

---

## Testing Implications

### Unit Tests

**Configuration Tests**:
- Test load with valid JSON
- Test load with corrupted JSON (should create defaults)
- Test load with missing fields (should use defaults)
- Test save creates readable file
- Test validation rules (bounds, types)

**ApplicationState Tests**:
- Test state transitions (stopped → running → stopped)
- Test error counting and auto-stop threshold
- Test movement count increments correctly

**MouseMovement Tests**:
- Mock mouse controller to test logic without actual movement
- Test alternating pattern generates correct deltas
- Test error handling on mouse control failure

### Integration Tests

**Configuration + State Tests**:
- Load config and verify state initialized correctly
- Change config and verify state updates
- Restart and verify state restored from `last_state`

**Timer + Movement Tests**:
- Verify movements occur at correct intervals (±10%)
- Verify movements stop when state set to stopped
- Verify error threshold triggers auto-stop

### System Tests

**End-to-End Tests**:
- Start application, verify idle timeout not reached after 2x interval
- Toggle running/stopped multiple times, verify state consistency
- Modify interval while running, verify change takes effect within 1 second
- Enable auto-start, restart system, verify application launches (manual test)

---

## Summary

The data model is intentionally minimal with only 5 core entities:
1. **Configuration**: User preferences (persisted)
2. **ApplicationState**: Runtime state (ephemeral)
3. **MouseMovement**: Movement operations (ephemeral)
4. **TrayIconState**: UI state (ephemeral)
5. **PlatformInfo**: Platform abstractions (runtime-detected)

This simplicity ensures:
- Easy to understand and maintain
- Minimal memory footprint
- Low complexity (no ORM, no database, no caching layers)
- Direct mapping to code structure (each entity = one module)

All entities are fully specified with validation rules, state transitions, and relationships clearly defined for implementation phase.
