# Installation Guide - Anti-Screensaver Mouse Mover (Windows)

This guide provides detailed installation instructions for Windows 10 and Windows 11.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [Method 1: Standalone Executable (Recommended)](#method-1-standalone-executable-recommended)
  - [Method 2: Python Source](#method-2-python-source)
- [Verification](#verification)
- [Building Executable from Source](#building-executable-from-source)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10 (64-bit) or Windows 11
- **RAM**: 100 MB available
- **Disk Space**: 50 MB for standalone executable, 200 MB for Python installation
- **Display**: Any resolution supported by Windows

### For Running from Source

- **Python**: Version 3.11 or higher
- **pip**: Latest version recommended

## Installation Methods

### Method 1: Standalone Executable (Recommended)

This method requires no Python installation and is the easiest way to get started.

#### Step 1: Download

1. Visit the [Releases page](https://github.com/yourusername/anti-screensaver/releases)
2. Download the latest `anti-screensaver.exe`
3. Optionally verify the SHA256 checksum (provided in release notes)

#### Step 2: Security Check

Windows SmartScreen may show a warning. This is normal for new applications:

1. Click "More info"
2. Click "Run anyway"

**Why this happens**: The application is not signed with a Microsoft-recognized certificate. The code is open source and can be audited.

#### Step 3: Run the Application

1. Double-click `anti-screensaver.exe`
2. The application will start and appear in your system tray (bottom-right)
3. Click the tray icon to open the main window

#### Step 4: Optional - Add to Startup

To make the application start with Windows:

1. Open the application main window
2. Check the "Start with Windows" checkbox
3. The application will now start automatically on boot

**Alternative manual method**:
1. Press `Win + R`
2. Type `shell:startup` and press Enter
3. Create a shortcut to `anti-screensaver.exe` in this folder
4. Right-click the shortcut → Properties
5. In "Target" field, add ` --minimized` at the end
6. Click OK

### Method 2: Python Source

This method is for developers or users who prefer to run from source.

#### Step 1: Install Python

1. Download Python 3.11 or higher from [python.org](https://www.python.org/downloads/windows/)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Complete the installation

Verify installation:
```cmd
python --version
```
Should show Python 3.11 or higher.

#### Step 2: Clone Repository

Using Git:
```cmd
git clone https://github.com/yourusername/anti-screensaver.git
cd anti-screensaver
```

Or download ZIP:
1. Visit the [repository](https://github.com/yourusername/anti-screensaver)
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file
4. Open Command Prompt in the extracted folder

#### Step 3: Create Virtual Environment (Recommended)

```cmd
python -m venv venv
venv\Scripts\activate
```

Your prompt should show `(venv)` prefix.

#### Step 4: Install Dependencies

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

Expected output: All packages installed successfully.

#### Step 5: Run the Application

```cmd
python -m src.main
```

To run minimized to tray:
```cmd
python -m src.main --minimized
```

#### Step 6: Create Desktop Shortcut (Optional)

1. Create a new file `anti-screensaver.bat` with this content:
   ```bat
   @echo off
   cd /d "C:\path\to\anti-screensaver"
   venv\Scripts\python.exe -m src.main
   ```
2. Right-click the .bat file → Create Shortcut
3. Move the shortcut to your Desktop

## Verification

After installation, verify the application is working:

### Test 1: Application Launches

1. The application should start without errors
2. A tray icon should appear (gray when stopped)
3. Clicking the tray icon should open the main window

### Test 2: Mouse Movement Works

1. Click "Start" in the main window
2. Wait 30 seconds without moving your mouse
3. You should see tiny cursor movements (1-2 pixels)
4. The tray icon should turn green

### Test 3: Configuration Saves

1. Change the interval slider to 60 seconds
2. Close and restart the application
3. The slider should still show 60 seconds

## Building Executable from Source

To create your own standalone executable:

### Prerequisites

```cmd
pip install -r requirements-dev.txt
```

### Build Process

1. Ensure you're in the project root directory
2. Run the build script:
   ```cmd
   build.bat
   ```

3. The executable will be created in `dist/anti-screensaver.exe`

### Build Script Details

The build script uses PyInstaller with these options:
- `--onefile`: Single executable file
- `--windowed`: No console window
- `--name anti-screensaver`: Output filename
- `--clean`: Clean PyInstaller cache before building

**Note**: Application icon is not currently configured. To add an icon in the future, place an `.ico` file at `assets/icon.ico` and add `--icon assets/icon.ico` to the PyInstaller command in `build.bat`.

### Verify Build

Test the built executable on a clean system:
1. Copy `dist/anti-screensaver.exe` to another Windows machine without Python
2. Run the executable
3. It should work without any dependencies

## Troubleshooting

### Issue: "Python not found" error

**Solution**:
1. Verify Python is installed: `python --version`
2. If not found, reinstall Python with "Add to PATH" checked
3. Restart Command Prompt after installation

### Issue: "pip install" fails with SSL errors

**Solution**:
```cmd
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Issue: ModuleNotFoundError when running

**Solution**:
1. Ensure virtual environment is activated: `venv\Scripts\activate`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Verify you're in the project root directory

### Issue: Qt platform plugin error

**Solution**:
1. Reinstall PySide6: `pip uninstall PySide6 && pip install PySide6`
2. Check Windows display settings are not set to "Headless" mode

### Issue: Mouse movements not working

**Solution**:
1. Ensure pynput is installed: `pip show pynput`
2. Check if antivirus is blocking the application
3. Run as administrator (right-click → Run as administrator)

### Issue: Auto-start registry modification fails

**Solution**:
1. Check if you're on a corporate/managed system (may restrict registry edits)
2. Try running as administrator
3. Use the manual startup folder method instead (see Method 1, Step 4)

### Issue: Antivirus blocks the application

**Solution**:
1. **For standalone exe**: Add exception in antivirus settings
2. **For source**: Antivirus typically doesn't flag Python scripts
3. Build from source yourself to verify safety
4. Submit to antivirus vendor for whitelisting if you believe it's a false positive

### Issue: Application doesn't minimize to tray

**Solution**:
1. Check Windows system tray settings (Settings → Personalization → Taskbar)
2. Ensure "Show hidden icons" is enabled
3. Look for the application icon in the hidden icons area

### Issue: High CPU usage

**Solution**:
1. Check interval setting (very low intervals like 1 second can cause high CPU)
2. Recommended minimum: 10 seconds
3. Restart the application

## Uninstallation

### For Standalone Executable

1. Right-click tray icon → Exit (if running)
2. Delete `anti-screensaver.exe`
3. Remove startup shortcut (if created):
   - Press `Win + R`
   - Type `shell:startup`
   - Delete the shortcut

4. Remove configuration file:
   - Press `Win + R`
   - Type `%APPDATA%\AntiScreensaver`
   - Delete the entire folder

5. Remove registry entry (if auto-start was enabled):
   - Press `Win + R`
   - Type `regedit`
   - Navigate to `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
   - Delete `AntiScreensaver` entry

### For Python Source Installation

1. Exit the application
2. Deactivate virtual environment: `deactivate`
3. Delete the project folder
4. Remove configuration (see step 4 above)
5. Remove registry entry (see step 5 above)

## Advanced Configuration

### Configuration File Location

```
%APPDATA%\AntiScreensaver\config.json
```

Typical path: `C:\Users\<YourUsername>\AppData\Roaming\AntiScreensaver\config.json`

### Manual Configuration Editing

You can manually edit the configuration file:

```json
{
  "interval_seconds": 30,
  "auto_start": false,
  "last_state": "stopped",
  "version": "1.0.0"
}
```

**Options**:
- `interval_seconds`: Number between 10 and 300
- `auto_start`: `true` or `false`
- `last_state`: `"running"` or `"stopped"`

**Note**: Restart the application after manual edits.

### Log Files

Logs are stored at:
```
%APPDATA%\AntiScreensaver\anti-screensaver.log
```

View logs to troubleshoot issues:
```cmd
type %APPDATA%\AntiScreensaver\anti-screensaver.log
```

## Getting Help

If you encounter issues not covered here:

1. Check the [main README](../README.md)
2. Search [existing issues](https://github.com/yourusername/anti-screensaver/issues)
3. Open a [new issue](https://github.com/yourusername/anti-screensaver/issues/new) with:
   - Windows version
   - Installation method
   - Error messages (if any)
   - Steps to reproduce

## Next Steps

After successful installation:

1. Read the [Usage Guide](../README.md#usage)
2. Configure your preferred interval
3. Set up auto-start if desired
4. Enjoy uninterrupted workflows!

---

**Last Updated**: 2024-12-01
