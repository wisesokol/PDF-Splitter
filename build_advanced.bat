@echo off
echo ========================================
echo PDF Splitter - Advanced Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again.
    pause
    exit /b 1
)

echo Step 1: Installing/upgrading PyInstaller...
python -m pip install --upgrade pyinstaller

echo.
echo Step 2: Installing dependencies...
python -m pip install -r requirements.txt

echo.
echo Step 3: Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo Step 4: Building Windows executable using spec file...
pyinstaller build.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\PDF_Splitter.exe
echo.
echo The executable is ready for distribution.
echo.
pause

