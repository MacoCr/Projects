@echo off
echo ====================================
echo  Building Spotify Display App
echo ====================================
echo.

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Build the executable
echo Building executable...
pyinstaller --name="Spotify Display" ^
    --onefile ^
    --windowed ^
    --icon=spotify_icon.ico ^
    --add-data=".env;." ^
    spotify_desktop_app.py

echo.
echo ====================================
echo Build complete!
echo ====================================
echo.
echo Your app is in the "dist" folder
echo Double-click "Spotify Display.exe" to run
echo.
pause