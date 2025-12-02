# Anti-Screensaver Mouse Mover

A lightweight Windows desktop application that prevents system idle/screensaver activation through imperceptible periodic mouse movements.

## Features

- 🖱️ **Micro Mouse Movements**: Moves cursor by 1-2 pixels to prevent idle detection
- 🎯 **Configurable Intervals**: Set movement frequency from 10-300 seconds
- 💻 **System Tray Integration**: Runs quietly in the background
- ⚙️ **Auto-Start Option**: Optionally start with Windows
- 🔒 **Privacy-First**: No data collection, no network activity
- 💾 **Lightweight**: <50MB RAM, <1% CPU usage

## Requirements

- Windows 10/11 or Linux (with X11/Wayland)
- Python 3.11+ (for running from source)
- OR standalone executable (no Python required, Windows only)

## Installation

### Option 1: Standalone Executable (Recommended)

1. Download `anti-screensaver.exe` from [Releases](https://github.com/yourusername/anti-screensaver/releases)
2. Run the executable
3. The application will appear in your system tray

### Option 2: Run from Source

1. Install Python 3.11 or higher
2. Clone this repository:
   ```cmd
   git clone https://github.com/yourusername/anti-screensaver.git
   cd anti-screensaver
   ```
3. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
4. Run the application:
   ```cmd
   python -m src.main
   ```

For detailed installation instructions, see [docs/INSTALL.md](docs/INSTALL.md).

## Usage

### Basic Usage

1. **Start the application** - Look for the icon in your system tray
2. **Click the tray icon** - Open the main window
3. **Click "Start"** - Enable mouse movement prevention
4. **Adjust interval** - Use the slider to change movement frequency
5. **Minimize to tray** - Close the window (app keeps running)

### Command Line Options

```cmd
# Start minimized to tray
anti-screensaver.exe --minimized

# Show help
anti-screensaver.exe --help
```

### System Tray Menu

Right-click the tray icon to access:
- **Start/Stop**: Toggle mouse movement
- **Show Window**: Open the main control window
- **Exit**: Quit the application

## Configuration

Settings are automatically saved to:
- **Windows**: `%APPDATA%\AntiScreensaver\config.json`
- **Linux**: `~/.config/anti-screensaver/config.json`
- **macOS**: `~/Library/Application Support/AntiScreensaver/config.json`

Default configuration:
- **Interval**: 30 seconds
- **Auto-start**: Disabled

## How It Works

The application uses a simple alternating pattern:
1. Move cursor +1 pixel right and +1 pixel down
2. Wait for configured interval
3. Move cursor -1 pixel left and -1 pixel up
4. Repeat

This keeps the system active while being imperceptible to users.

## Privacy & Security

- ✅ **No data collection**: Zero telemetry or analytics
- ✅ **No network activity**: Application works completely offline
- ✅ **No keylogging**: Only mouse movements, no keyboard monitoring
- ✅ **User-level permissions**: No administrator rights required
- ✅ **Open source**: Full transparency, audit the code yourself

## Troubleshooting

### Mouse movements don't prevent lock screen

- Check your Windows idle timeout settings (Settings → System → Power & Sleep)
- Ensure interval is shorter than your system's idle timeout
- Verify the application shows "Running" status in the tray

### Application won't start

- Ensure you have Windows 10/11 or Linux
- For standalone exe: No additional requirements (Windows only)
- For source: Verify Python 3.11+ is installed
- On Linux: Ensure you have X11 or a compatible Wayland compositor

### Antivirus false positive

Some antivirus software may flag mouse automation tools. The application is safe and open source. You can:
- Add an exception in your antivirus
- Build from source yourself to verify
- Review the code on GitHub

### Auto-start doesn't work

- Check if your corporate/managed system restricts registry modifications
- Verify the checkbox is enabled in the application settings
- Check Windows Task Manager → Startup tab for the entry

For more help, see [docs/INSTALL.md](docs/INSTALL.md) or [open an issue](https://github.com/yourusername/anti-screensaver/issues).

## Building from Source

To create a standalone executable:

```cmd
# Install build dependencies
pip install -r requirements-dev.txt

# Build executable
build.bat

# Output: dist/anti-screensaver.exe
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is intended for legitimate use cases such as:
- Preventing interruptions during remote presentations
- Monitoring long-running processes
- Maintaining active sessions during authorized work

Users are responsible for ensuring compliance with their organization's policies.

## Acknowledgments

Built with:
- [PySide6](https://www.qt.io/qt-for-python) - Qt for Python GUI framework
- [pynput](https://github.com/moses-palmer/pynput) - Cross-platform input control
- [fasteners](https://github.com/harlowja/fasteners) - File-based locks

---

**Made with ❤️ for uninterrupted workflows**
