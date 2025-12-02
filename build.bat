@echo off
REM ============================================================================
REM Anti-Screensaver Mouse Mover - Windows Build Script
REM ============================================================================
REM This script creates a standalone Windows executable using PyInstaller.
REM No Python installation required to run the resulting executable.
REM
REM Requirements:
REM   - Python 3.11+ installed and in PATH
REM   - PyInstaller installed (pip install -r requirements-dev.txt)
REM
REM Output: dist/anti-screensaver.exe
REM ============================================================================

echo.
echo ============================================================================
echo Anti-Screensaver Mouse Mover - Build Script
echo ============================================================================
echo.

REM Check if Python is available
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    echo Please install Python 3.11+ and ensure it's added to PATH
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

REM Check if PyInstaller is installed
echo [2/6] Checking PyInstaller installation...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller not found
    echo Please install development dependencies:
    echo   pip install -r requirements-dev.txt
    pause
    exit /b 1
)
python -c "import PyInstaller; print('PyInstaller version:', PyInstaller.__version__)"
echo.

REM Check if entry point exists
echo [3/6] Verifying source files...
if not exist "src\main.py" (
    echo ERROR: Entry point src\main.py not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)
echo Entry point found: src\main.py
echo.

REM Clean previous build artifacts
echo [4/6] Cleaning previous build artifacts...
if exist "dist" (
    echo Removing dist\ directory...
    rmdir /s /q "dist"
)
if exist "build" (
    echo Removing build\ directory...
    rmdir /s /q "build"
)
if exist "anti-screensaver.spec" (
    echo Removing old spec file...
    del /q "anti-screensaver.spec"
)
echo Clean complete.
echo.

REM Run PyInstaller
echo [5/6] Building executable with PyInstaller...
echo This may take 1-2 minutes...
echo.

python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name anti-screensaver ^
    --clean ^
    src/main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the error messages above for details.
    pause
    exit /b 1
)
echo.

REM Verify output
echo [6/6] Verifying build output...
if not exist "dist\anti-screensaver.exe" (
    echo ERROR: Expected output file not found: dist\anti-screensaver.exe
    echo Build may have failed silently.
    pause
    exit /b 1
)

REM Get file size
for %%A in ("dist\anti-screensaver.exe") do set size=%%~zA
set /a sizeMB=size/1024/1024

echo.
echo ============================================================================
echo BUILD SUCCESSFUL!
echo ============================================================================
echo.
echo Executable created: dist\anti-screensaver.exe
echo File size: %sizeMB% MB
echo.
echo You can now distribute this file. It runs without Python installed.
echo.
echo Next steps:
echo   1. Test the executable: dist\anti-screensaver.exe
echo   2. Check functionality (GUI, mouse movement, tray icon)
echo   3. Distribute to users
echo.
echo ============================================================================
echo.

pause
