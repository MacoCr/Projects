@echo off
title Spotify Display

echo.
echo ====================================
echo    Spotify Display Launcher
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from python.org
    pause
    exit /b 1
)

REM Run the launcher
python launch_spotify_display.py

pause