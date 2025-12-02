# Research: Anti-Screensaver Mouse Mover

**Feature**: 001-anti-screensaver-mouse-mover
**Date**: 2024-12-01
**Status**: Complete

## Overview

This document resolves all technical uncertainties identified in the Technical Context section of the implementation plan. Each research area includes the decision made, rationale, and alternatives considered.

---

## 1. Programming Language Selection

### Decision: Python 3.11+

### Rationale:
- **Cross-platform GUI support**: Mature frameworks (PyQt6, PySide6, tkinter) with excellent documentation
- **Mouse control libraries**: `pynput` and `pyautogui` provide simple, reliable cross-platform mouse manipulation
- **Rapid development**: Shorter development cycle for MVP, easier prototyping
- **Low barrier to contribution**: More developers familiar with Python for future maintenance
- **Performance acceptable**: For this use case (<1% CPU, <50MB RAM), Python's overhead is negligible
- **System tray integration**: Well-supported through `pystray` or Qt system tray classes

### Alternatives Considered:
1. **Rust**
   - **Pros**: Minimal resource usage (~5-10MB RAM), excellent performance, no GC pauses
   - **Cons**: Steeper learning curve, fewer mature GUI options (egui/iced still maturing), longer development time, smaller talent pool for maintenance
   - **Rejected because**: Performance gains unnecessary for this use case; MVP speed more important

2. **Go**
   - **Pros**: Simple syntax, good performance, single binary distribution
   - **Cons**: GUI ecosystem less mature than Python (fyne is main option), CGo required for some system calls adds complexity
   - **Rejected because**: Python's GUI ecosystem is significantly more mature and better documented

3. **Electron (JavaScript/TypeScript)**
   - **Pros**: Rich UI possibilities, large developer community, cross-platform
   - **Cons**: 80-150MB RAM overhead (fails NFR-002: <50MB requirement), large distribution size (~100MB)
   - **Rejected because**: Violates memory constraints by 60-200%

---

## 2. GUI Framework Selection

### Decision: PySide6 (Qt for Python)

### Rationale:
- **Native look and feel**: Qt renders native widgets on all platforms
- **System tray support**: Excellent built-in system tray integration (`QSystemTrayIcon`)
- **Comprehensive widgets**: Includes sliders, checkboxes, buttons needed for configuration UI
- **Signal/slot architecture**: Clean event handling pattern
- **License**: LGPL-friendly for open-source and commercial use
- **Documentation**: Extensive official documentation and community resources
- **Performance**: Lightweight compared to Electron, meets <50MB RAM requirement

### Alternatives Considered:
1. **PyQt6**
   - **Pros**: Nearly identical to PySide6 in functionality
   - **Cons**: GPL license or commercial license required (PySide6 LGPL is more permissive)
   - **Rejected because**: License constraints for potential future commercial use

2. **tkinter**
   - **Pros**: Bundled with Python, no extra dependencies, very lightweight
   - **Cons**: System tray support limited/awkward, dated appearance, less professional look
   - **Rejected because**: Poor system tray support is critical missing feature

3. **wxPython**
   - **Pros**: Native widgets, good system tray support
   - **Cons**: Less active development than Qt, smaller community, documentation not as comprehensive
   - **Rejected because**: Qt has better long-term support and documentation

---

## 3. Mouse Control Library Selection

### Decision: `pynput`

### Rationale:
- **Cross-platform**: Works on Linux (X11, Wayland), Windows, macOS with single API
- **Precise control**: Supports relative pixel movements (`controller.move(dx, dy)`)
- **Lightweight**: Pure Python with minimal dependencies
- **Non-intrusive**: Does not interfere with user's natural mouse movement
- **Active maintenance**: Regular updates and bug fixes
- **No UI dependencies**: Can run headless if needed for future CLI mode

### Alternatives Considered:
1. **pyautogui**
   - **Pros**: Simple API, includes screenshot capabilities
   - **Cons**: Absolute positioning focus (not ideal for micro-movements), slower than pynput, includes unnecessary features (screenshot, image recognition)
   - **Rejected because**: Overkill for simple mouse movements; pynput is more focused

2. **Direct X11/Xlib calls (Linux-specific)**
   - **Pros**: No external dependencies, maximum control
   - **Cons**: Platform-specific implementation per OS, more complex code, no Wayland support without additional work
   - **Rejected because**: Cross-platform goal requires abstraction anyway; pynput provides this

3. **python-xlib**
   - **Pros**: Low-level control on Linux
   - **Cons**: Linux X11 only, no Windows/macOS support, more complex API
   - **Rejected because**: Too platform-specific for cross-platform goals

---

## 4. Configuration Storage Format

### Decision: JSON with `config.json` file

### Rationale:
- **Human-readable**: Users can manually edit if needed
- **Standard library support**: `json` module built into Python, no dependencies
- **Simple structure**: Configuration is flat with few nested values
- **Validation straightforward**: Easy to validate with simple Python dictionaries
- **Cross-platform**: Works identically on all operating systems

### Configuration Schema:
```json
{
  "interval_seconds": 30,
  "auto_start": false,
  "last_state": "stopped",
  "version": "1.0.0"
}
```

### Alternatives Considered:
1. **TOML**
   - **Pros**: More human-friendly for complex configs, supports comments
   - **Cons**: Requires external library (`tomli`/`tomllib` only in Python 3.11+), overkill for simple config
   - **Rejected because**: JSON is simpler and meets all needs; no complex nesting required

2. **YAML**
   - **Pros**: Very human-readable, supports comments
   - **Cons**: Requires `PyYAML` dependency, security concerns with unsafe loading
   - **Rejected because**: Unnecessary complexity and dependency for simple config

3. **INI format**
   - **Pros**: Simple, `configparser` in standard library
   - **Cons**: Less structured than JSON, harder to validate, less modern
   - **Rejected because**: JSON provides better structure and validation

---

## 5. Testing Framework Selection

### Decision: `pytest` with `pytest-qt` plugin

### Rationale:
- **Industry standard**: Most widely used Python testing framework
- **Rich plugin ecosystem**: `pytest-qt` enables GUI testing without manual event simulation
- **Fixtures**: Clean test setup/teardown with dependency injection
- **Parameterization**: Easy to test multiple configurations (different intervals, etc.)
- **Coverage integration**: Works seamlessly with `pytest-cov` for code coverage reports
- **Async support**: Can test timer-based behavior with `pytest-asyncio` if needed

### Test Structure:
- **Unit tests**: Test individual components (config manager, state tracker) in isolation
- **Integration tests**: Test GUI interactions with core logic using `pytest-qt` `qtbot` fixture
- **System tests**: End-to-end tests verifying idle prevention works (may require test harness)

### Alternatives Considered:
1. **unittest**
   - **Pros**: Standard library, no dependencies
   - **Cons**: More verbose, less powerful fixtures, weaker assertion introspection
   - **Rejected because**: pytest provides better developer experience and GUI testing support

2. **nose2**
   - **Pros**: Extension of unittest with some pytest-like features
   - **Cons**: Less active development than pytest, smaller plugin ecosystem
   - **Rejected because**: pytest is more actively maintained and has better Qt support

---

## 6. Linux Mouse Control Implementation Details

### Decision: `pynput.mouse.Controller` with X11/Wayland compatibility layer

### Rationale:
- **Wayland compatibility**: `pynput` detects display server and uses appropriate backend
- **X11 support**: Uses Xlib under the hood for X11 systems
- **Minimal privileges**: Does not require root or special permissions
- **Relative movements**: `controller.move(1, 0)` moves 1 pixel right, perfect for micro-movements

### Implementation Pattern:
```python
from pynput.mouse import Controller

mouse = Controller()
# Move 1 pixel right and 1 pixel down
mouse.move(1, 1)
# Return to original position
mouse.move(-1, -1)
```

### Alternatives Considered:
1. **python-xlib directly**
   - **Pros**: More control, no middleman library
   - **Cons**: X11 only, no Wayland support, more complex code
   - **Rejected because**: pynput abstracts display server differences

2. **xdotool via subprocess**
   - **Pros**: Simple command-line tool
   - **Cons**: External dependency (not pure Python), subprocess overhead, less precise control
   - **Rejected because**: subprocess overhead defeats performance goals; pynput is more efficient

---

## 7. Auto-Start Implementation Strategy

### Decision: Platform-specific auto-start with abstraction layer

### Linux Implementation:
- **Method**: Create `.desktop` file in `~/.config/autostart/`
- **File location**: `~/.config/autostart/anti-screensaver.desktop`
- **Format**: XDG autostart specification

### Example Desktop Entry:
```ini
[Desktop Entry]
Type=Application
Name=Anti-Screensaver Mouse Mover
Exec=/usr/bin/python3 /path/to/anti-screensaver/main.py --minimized
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

### Future Windows Implementation:
- Create registry entry in `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- Or create shortcut in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\`

### Future macOS Implementation:
- Create Launch Agent plist in `~/Library/LaunchAgents/`

### Alternatives Considered:
1. **System service/daemon**
   - **Pros**: More robust, survives crashes
   - **Cons**: Requires root, overkill for user-level utility, harder to install/uninstall
   - **Rejected because**: User-level autostart is sufficient and simpler

2. **Systemd user unit (Linux)**
   - **Pros**: Modern Linux standard, logging built-in
   - **Cons**: Linux-specific, doesn't work on all distros, requires systemctl knowledge
   - **Rejected because**: `.desktop` autostart is more universal across desktop environments

---

## 8. Single Instance Prevention Strategy

### Decision: PID file lock with `fasteners` library

### Rationale:
- **Cross-platform**: Works on Linux, Windows, macOS
- **Atomic lock**: File locking is atomic at OS level
- **Automatic cleanup**: Lock released when process terminates
- **Simple API**: `InterProcessLock` class handles complexity

### Implementation Pattern:
```python
import fasteners
import sys

lock = fasteners.InterProcessLock('/tmp/anti-screensaver.lock')
if not lock.acquire(blocking=False):
    print("Another instance is already running")
    sys.exit(1)
# Application continues...
# Lock automatically released on exit
```

### Alternatives Considered:
1. **Socket-based lock**
   - **Pros**: No file system dependency
   - **Cons**: More complex, requires handling cleanup, port conflicts possible
   - **Rejected because**: File locks are simpler and more reliable

2. **Qt single application**
   - **Pros**: Built into Qt framework
   - **Cons**: Heavier weight, requires Qt to initialize before check
   - **Rejected because**: Want to check before initializing GUI

3. **psutil process scanning**
   - **Pros**: No lock file needed
   - **Cons**: Race conditions possible, process name matching unreliable
   - **Rejected because**: Not atomic; can miss race conditions

---

## 9. Timer/Scheduling Strategy

### Decision: Qt `QTimer` for periodic mouse movements

### Rationale:
- **Integrated with event loop**: No threading complexity
- **Millisecond precision**: Can set intervals from 10-300 seconds precisely
- **Start/stop control**: `timer.start()` and `timer.stop()` provide instant control
- **Signal-based**: Connects cleanly to mouse movement callback
- **Low overhead**: Single-shot or repeating timers with minimal resource usage

### Implementation Pattern:
```python
from PySide6.QtCore import QTimer

self.timer = QTimer()
self.timer.timeout.connect(self.move_mouse)
self.timer.start(30000)  # 30 seconds in milliseconds
```

### Alternatives Considered:
1. **threading.Timer**
   - **Pros**: Standard library, no Qt dependency
   - **Cons**: Thread per timer, higher overhead, not integrated with GUI event loop
   - **Rejected because**: Threading adds complexity; Qt timer is more efficient

2. **asyncio.sleep loop**
   - **Pros**: Modern async approach
   - **Cons**: Requires running async event loop alongside Qt event loop (complex integration)
   - **Rejected because**: Dual event loops add significant complexity

3. **time.sleep in background thread**
   - **Pros**: Simple to understand
   - **Cons**: Dedicated thread overhead, harder to start/stop instantly, not responsive
   - **Rejected because**: QTimer is more responsive and lighter

---

## 10. System Sleep/Wake Handling

### Decision: Monitor system signals using Qt or D-Bus (Linux)

### Linux Implementation:
- **Method**: Listen to D-Bus signals from systemd-logind or UPower
- **Signals**: `PrepareForSleep`, `Resuming` signals
- **Action**: Pause timer on sleep, resume on wake

### Implementation Pattern (using dbus-python):
```python
import dbus
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
bus.add_signal_receiver(
    self.on_sleep_prepare,
    signal_name='PrepareForSleep',
    dbus_interface='org.freedesktop.login1.Manager',
    path='/org/freedesktop/login1'
)
```

### Alternatives Considered:
1. **No sleep handling**
   - **Pros**: Simplest implementation
   - **Cons**: Timer continues during sleep, wasted CPU cycles, potential confusion
   - **Rejected because**: Professional polish requires proper sleep handling

2. **Polling system uptime**
   - **Pros**: No D-Bus dependency
   - **Cons**: Polling overhead, delayed detection, inaccurate
   - **Rejected because**: Signal-based approach is cleaner and more efficient

---

## 11. Error Handling and Logging Strategy

### Decision: Python `logging` module with file + console output

### Rationale:
- **Standard library**: No external dependencies
- **Configurable levels**: DEBUG, INFO, WARNING, ERROR for different scenarios
- **Multiple handlers**: Can log to file for troubleshooting and console for development
- **Rotation**: `RotatingFileHandler` prevents log files from growing unbounded
- **Performance**: Minimal overhead when logging disabled

### Log Configuration:
- **File location**: `~/.config/anti-screensaver/anti-screensaver.log` (Linux)
- **Default level**: INFO in production, DEBUG available via command-line flag
- **Rotation**: Max 5MB per file, keep 3 backups
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### What to Log:
- Application start/stop
- Configuration changes
- Mouse movement execution (DEBUG level)
- Errors (file access, mouse control failures)
- Timer start/stop events

### Alternatives Considered:
1. **loguru**
   - **Pros**: More modern API, colored output, automatic rotation
   - **Cons**: External dependency, overkill for simple use case
   - **Rejected because**: Standard logging is sufficient; avoid unnecessary dependencies

2. **Print statements only**
   - **Pros**: Simplest possible
   - **Cons**: No levels, no file output, hard to disable, unprofessional
   - **Rejected because**: Proper logging is essential for debugging user issues

---

## 12. Distribution and Packaging Strategy

### Decision: Multi-method distribution approach

### Primary Distribution Methods:

1. **PyPI Package (pip installable)**
   - **Target**: Python developers, power users
   - **Installation**: `pip install anti-screensaver`
   - **Pros**: Standard Python distribution, easy updates via pip
   - **Cons**: Requires Python installed, less accessible to non-technical users

2. **Standalone Executable (PyInstaller)**
   - **Target**: End users without Python
   - **Platforms**: Separate binaries for Linux (AppImage), Windows (EXE), macOS (DMG)
   - **Pros**: No Python installation required, double-click to run
   - **Cons**: Larger file size (~30-50MB), separate builds per platform

3. **Source Distribution (GitHub)**
   - **Target**: Developers, contributors
   - **Installation**: `git clone` + `pip install -e .`
   - **Pros**: Full source access, easy contributions
   - **Cons**: Requires Python and Git knowledge

### Recommended MVP Approach:
Start with **source distribution** and **PyPI package** for v1.0, add standalone executables in v1.1 based on user feedback.

### Alternatives Considered:
1. **Snap/Flatpak (Linux)**
   - **Pros**: Sandboxed, auto-updates, universal Linux package
   - **Cons**: Larger size, slower startup, sandboxing may complicate mouse control
   - **Rejected for MVP because**: Adds packaging complexity; revisit post-MVP

2. **Docker container**
   - **Pros**: Consistent environment
   - **Cons**: Cannot access host display/mouse easily, not suitable for desktop apps
   - **Rejected because**: Fundamentally incompatible with desktop GUI requirements

---

## Summary of Technology Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Language | Python | 3.11+ | Mature ecosystem, rapid development, cross-platform GUI support |
| GUI Framework | PySide6 | 6.x | Native widgets, excellent system tray, LGPL license |
| Mouse Control | pynput | 1.7+ | Cross-platform, lightweight, precise control |
| Testing | pytest + pytest-qt | latest | Industry standard, GUI testing support |
| Timer | QTimer | (PySide6) | Integrated event loop, no threading complexity |
| Config Format | JSON | stdlib | Simple, human-readable, no dependencies |
| Single Instance | fasteners | 0.18+ | Cross-platform file locking |
| Logging | logging | stdlib | Standard, configurable, sufficient for needs |
| Packaging | PyPI + PyInstaller | latest | Accessible to both developers and end users |

---

## Risk Mitigation

### Identified Risks:

1. **Wayland compatibility issues**
   - **Risk**: Some Wayland compositors restrict input simulation
   - **Mitigation**: Test on multiple Wayland environments (GNOME, KDE), document limitations, provide X11 fallback instructions

2. **Permission issues on restrictive systems**
   - **Risk**: Corporate/enterprise systems may block input simulation
   - **Mitigation**: Document requirements, provide diagnostic tool to test mouse control, add clear error messages

3. **Qt licensing confusion**
   - **Risk**: Users may confuse PySide6 LGPL with PyQt GPL
   - **Mitigation**: Clear documentation of license choice, LICENSE file in repository

4. **Performance degradation over time**
   - **Risk**: Memory leaks or timer drift during extended operation
   - **Mitigation**: Comprehensive long-running tests (24+ hour soak tests), memory profiling

5. **False sense of security**
   - **Risk**: Users may violate company policies thinking this tool is undetectable
   - **Mitigation**: Clear disclaimer in documentation that tool is for legitimate use cases (long-running processes, meetings), not policy circumvention

---

## Next Steps (Phase 1)

With research complete, proceed to:
1. **Data Model Design** (data-model.md): Define configuration schema, state transitions, entity relationships
2. **Contract Design** (contracts/): Define internal APIs between components (core, GUI, platform layers)
3. **Quickstart Guide** (quickstart.md): Document how to run tests, build, and develop

All "NEEDS CLARIFICATION" items from Technical Context are now resolved.
