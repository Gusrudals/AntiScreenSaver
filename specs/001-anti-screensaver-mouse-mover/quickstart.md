# Developer Quickstart Guide

**Feature**: 001-anti-screensaver-mouse-mover
**Date**: 2024-12-01

## Overview

This guide helps developers quickly set up, build, test, and develop the Anti-Screensaver Mouse Mover application. Follow these steps to get from zero to running application in under 10 minutes.

---

## Prerequisites

### Required

- **Python**: 3.11 or higher
  - Check: `python3 --version`
  - Install: [python.org/downloads](https://www.python.org/downloads/)

- **pip**: Python package manager (usually included with Python)
  - Check: `pip3 --version`

- **Git**: Version control
  - Check: `git --version`
  - Install: [git-scm.com](https://git-scm.com/)

### Recommended

- **Virtual environment tool**: `venv` (included with Python)
- **Code editor**: VS Code, PyCharm, or similar with Python support
- **Linux system**: MVP targets Linux; Windows/macOS support in future versions

### Platform-Specific Requirements

**Linux**:
- X11 or Wayland display server
- Development libraries: `sudo apt install python3-dev libxcb-xinerama0` (Ubuntu/Debian)
- For Wayland: Ensure compositor allows input simulation

**Windows** (Future):
- Windows 10/11
- Microsoft Visual C++ Build Tools (for some dependencies)

**macOS** (Future):
- macOS 11+ (Big Sur or later)
- Xcode Command Line Tools: `xcode-select --install`

---

## Quick Setup (5 minutes)

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/anti-screensaver.git
cd anti-screensaver
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows
```

**Verify activation**: Your prompt should show `(venv)` prefix.

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install application dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

**Expected dependencies** (from research phase):
```txt
# requirements.txt
PySide6>=6.6.0
pynput>=1.7.6
fasteners>=0.18

# requirements-dev.txt
pytest>=7.4.0
pytest-qt>=4.2.0
pytest-cov>=4.1.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.5.0
```

### 4. Verify Installation

```bash
# Run test to verify setup
python -m pytest tests/ -v

# Expected output: All tests pass (or test suite empty initially)
```

---

## Project Structure

```
anti-screensaver/
├── src/                     # Application source code
│   ├── core/               # Core business logic
│   │   ├── mouse_mover.py  # Mouse movement engine
│   │   ├── config.py       # Configuration manager
│   │   └── state.py        # State manager
│   ├── gui/                # GUI components
│   │   ├── main_window.py  # Main window
│   │   ├── tray_icon.py    # System tray icon
│   │   └── widgets.py      # Reusable widgets
│   ├── platform/           # Platform-specific code
│   │   ├── linux.py        # Linux mouse control
│   │   ├── windows.py      # Windows mouse control (future)
│   │   └── macos.py        # macOS mouse control (future)
│   └── main.py             # Entry point
│
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── system/             # End-to-end tests
│
├── config/                  # Configuration files
│   └── default_config.json # Default configuration
│
├── specs/                   # Design documents
│   └── 001-anti-screensaver-mouse-mover/
│       ├── spec.md         # Feature specification
│       ├── plan.md         # Implementation plan
│       ├── research.md     # Technology research
│       ├── data-model.md   # Data model design
│       ├── quickstart.md   # This file
│       └── contracts/      # API contracts
│
├── docs/                    # User documentation
│   ├── README.md           # User guide
│   └── INSTALL.md          # Installation instructions
│
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml          # Project configuration
├── setup.py                # Package setup
└── README.md               # Project overview
```

---

## Development Workflow

### Running the Application

```bash
# From project root
python -m src.main

# With debug logging
python -m src.main --debug

# Start minimized to tray
python -m src.main --minimized
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py

# Run specific test
pytest tests/unit/test_config.py::test_load_valid_config

# Run with verbose output
pytest -v

# Run and show print statements
pytest -s
```

### Code Quality Checks

```bash
# Format code with black
black src/ tests/

# Lint code with flake8
flake8 src/ tests/

# Type check with mypy
mypy src/

# Run all quality checks
./scripts/check_quality.sh  # (to be created)
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, commit
git add .
git commit -m "Description of changes"

# Push and create pull request
git push origin feature/your-feature-name
```

---

## Building and Packaging

### Development Build

```bash
# Install in editable mode
pip install -e .

# Now you can run from anywhere
anti-screensaver
```

### Creating Standalone Executable (PyInstaller)

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile \
            --windowed \
            --name anti-screensaver \
            --icon assets/icon.ico \
            src/main.py

# Output in dist/ directory
./dist/anti-screensaver
```

### Creating PyPI Package

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Upload to PyPI (production)
twine upload dist/*

# Upload to Test PyPI (for testing)
twine upload --repository testpypi dist/*
```

---

## Testing Guide

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_config.py       # Configuration manager tests
│   ├── test_state.py        # State manager tests
│   └── test_mouse_mover.py  # Movement engine tests
├── integration/             # Integration tests (multiple components)
│   ├── test_gui_integration.py
│   └── test_platform_integration.py
└── system/                  # End-to-end tests (full application)
    └── test_idle_prevention.py
```

### Writing Tests

**Example Unit Test**:
```python
# tests/unit/test_config.py
import pytest
from src.core.config import ConfigurationManager

def test_load_default_config():
    """Test loading default configuration when no file exists."""
    mgr = ConfigurationManager()
    config = mgr.load()

    assert config.interval_seconds == 30
    assert config.auto_start is False
    assert config.last_state == "stopped"

def test_validate_interval_bounds():
    """Test interval validation rejects out-of-bounds values."""
    mgr = ConfigurationManager()
    config = mgr.create_default()
    config.interval_seconds = 5  # Too low

    errors = config.validate()
    assert len(errors) > 0
    assert "interval_seconds" in errors[0]
```

**Example Integration Test** (with pytest-qt):
```python
# tests/integration/test_gui_integration.py
import pytest
from pytestqt.qtbot import QtBot
from src.gui.main_window import MainWindow

def test_start_button_triggers_movement(qtbot):
    """Test clicking start button activates movement engine."""
    window = MainWindow()
    qtbot.addWidget(window)

    # Find start button and click it
    start_btn = window.findChild(QPushButton, "startButton")
    qtbot.mouseClick(start_btn, Qt.LeftButton)

    # Verify state changed
    assert window.controller.is_running() is True
```

### Test Fixtures

**Common fixtures** (in `tests/conftest.py`):
```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_mouse_controller():
    """Provide mock mouse controller for testing."""
    controller = Mock()
    controller.move.return_value = MouseMovement(
        delta_x=1, delta_y=1,
        timestamp=datetime.now(),
        success=True
    )
    return controller

@pytest.fixture
def temp_config_file(tmp_path):
    """Provide temporary config file for testing."""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"interval_seconds": 30, "auto_start": false}')
    return str(config_file)
```

---

## Debugging Tips

### Enable Debug Logging

```bash
# Set environment variable
export ANTI_SCREENSAVER_LOG_LEVEL=DEBUG

# Run application
python -m src.main
```

### Common Issues

**Issue**: "Permission denied" when moving mouse
- **Solution**: Check if running on Wayland; may need X11 fallback
- **Test**: `echo $XDG_SESSION_TYPE` should show `x11` or `wayland`

**Issue**: "Another instance is running"
- **Solution**: Remove lock file: `rm /tmp/anti-screensaver.lock`
- **Prevention**: Ensure proper cleanup in exception handlers

**Issue**: Tests fail with "QApplication not found"
- **Solution**: Install `pytest-qt`: `pip install pytest-qt`
- **Verify**: `pytest --version` should show `pytest-qt` plugin

**Issue**: Import errors for `src` module
- **Solution**: Run from project root, not from `src/` directory
- **Or**: Install in editable mode: `pip install -e .`

### Debugging Mouse Control

```python
# Test mouse control directly
from src.platform.linux import LinuxMouseController

controller = LinuxMouseController()
print(f"Current position: {controller.get_current_position()}")

movement = controller.move(1, 1)
print(f"Movement success: {movement.success}")
print(f"New position: {controller.get_current_position()}")
```

---

## IDE Setup

### VS Code

**Recommended extensions**:
- Python (Microsoft)
- Pylance
- Python Test Explorer
- Better Comments

**Workspace settings** (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true
}
```

### PyCharm

1. **Set interpreter**: File → Settings → Project → Python Interpreter → Add → Virtualenv Environment → Existing → `venv/bin/python`
2. **Enable pytest**: Settings → Tools → Python Integrated Tools → Testing → Default test runner: pytest
3. **Configure code style**: Settings → Editor → Code Style → Python → Set from: PEP 8

---

## Performance Profiling

### CPU Profiling

```bash
# Install profiler
pip install py-spy

# Profile running application
py-spy record -o profile.svg -- python -m src.main

# View profile.svg in browser
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Add @profile decorator to functions
# Run with profiler
python -m memory_profiler src/main.py
```

### Load Testing

```python
# tests/performance/test_long_running.py
import time
import pytest

def test_24_hour_stability():
    """Test application runs stably for 24 hours (manual test)."""
    # This is a manual test, not part of CI
    from src.main import Application

    app = Application()
    app.start_movement()

    # Run for 24 hours
    time.sleep(24 * 60 * 60)

    # Check metrics
    state = app.get_state()
    assert state.error_count < 10  # Less than 10 errors in 24h
    assert state.movement_count > (24 * 60 * 2)  # At least 2/min avg
```

---

## Contributing

### Before Submitting PR

1. **Run tests**: `pytest`
2. **Check coverage**: `pytest --cov=src --cov-report=term-missing`
3. **Format code**: `black src/ tests/`
4. **Lint code**: `flake8 src/ tests/`
5. **Type check**: `mypy src/`
6. **Update docs**: If API changes, update relevant documentation

### PR Checklist

- [ ] Tests pass (`pytest`)
- [ ] Coverage >80% for new code
- [ ] Code formatted with `black`
- [ ] No linting errors
- [ ] Type hints added
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Commit messages follow convention

---

## Useful Commands Reference

```bash
# Development
python -m src.main                    # Run application
python -m src.main --debug            # Debug mode
pytest                                # Run tests
pytest --cov=src                      # Test with coverage
black src/ tests/                     # Format code
flake8 src/ tests/                    # Lint code
mypy src/                             # Type check

# Building
pip install -e .                      # Install editable
python -m build                       # Build package
pyinstaller src/main.py              # Create executable

# Profiling
py-spy record -- python -m src.main   # CPU profile
python -m memory_profiler src/main.py # Memory profile

# Cleanup
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache .mypy_cache .coverage htmlcov/
```

---

## Next Steps

1. **Read the architecture**: Review `contracts/README.md` to understand component interfaces
2. **Explore data model**: See `data-model.md` for entity details
3. **Check implementation plan**: Read `plan.md` for overall strategy
4. **Start coding**: Begin with `src/core/config.py` (simplest component)
5. **Write tests first**: Follow TDD approach (tests → fail → implement → pass)

---

## Getting Help

- **Documentation**: Check `specs/` directory for design docs
- **Code examples**: See `tests/` for usage examples
- **Issues**: Search existing issues on GitHub
- **Questions**: Open a discussion on GitHub Discussions

---

## Troubleshooting

### Virtual Environment Issues

```bash
# If venv activation fails
deactivate  # Exit current venv if any
rm -rf venv  # Remove corrupted venv
python3 -m venv venv  # Recreate
source venv/bin/activate
pip install -r requirements.txt
```

### Dependency Conflicts

```bash
# Clean install
pip freeze > current_deps.txt  # Backup current
pip uninstall -y -r current_deps.txt  # Remove all
pip install -r requirements.txt  # Fresh install
```

### Qt/GUI Issues on Linux

```bash
# Install Qt dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0  # Ubuntu/Debian
sudo dnf install xcb-util-cursor  # Fedora

# If still failing, try X11 mode
export QT_QPA_PLATFORM=xcb
python -m src.main
```

---

**Last Updated**: 2024-12-01
**Maintained By**: Development Team
**Questions**: Open an issue on GitHub
