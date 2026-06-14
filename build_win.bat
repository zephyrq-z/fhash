@echo off
REM Build fhash Windows .exe using PyInstaller
REM Run this on a Windows machine with Python 3.10+ installed.

echo Building fhash for Windows...

REM Check PyInstaller
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build .exe
pyinstaller ^
    --name "fhash" ^
    --windowed ^
    --onefile ^
    --clean ^
    --noconfirm ^
    --icon assets/icon.ico ^
    fhash_gui.py

echo.
echo Build complete!
echo   Executable: dist\fhash.exe
echo.
pause
