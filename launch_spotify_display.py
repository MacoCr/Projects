import subprocess
import webbrowser
import time
import sys
import os
from pathlib import Path

def main():
    print("🎵 Starting Spotify Display App...")
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    main_script = script_dir / "spotify_display.py"
    
    # Check if spotify_display.py exists
    if not main_script.exists():
        print("❌ Error: spotify_display.py not found!")
        print(f"   Looking in: {script_dir}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check if .env exists
    env_file = script_dir / ".env"
    if not env_file.exists():
        print("❌ Error: .env file not found!")
        print("   Please create a .env file with your Spotify credentials")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print("✅ Found spotify_display.py")
    print("✅ Found .env file")
    print("\n🚀 Starting server...")
    
    # Start the Flask server as a subprocess
    try:
        # Start server without showing console window on Windows
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(
                [sys.executable, str(main_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo
            )
        else:
            process = subprocess.Popen(
                [sys.executable, str(main_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        # Wait a few seconds for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is not None:
            print("❌ Server failed to start!")
            stdout, stderr = process.communicate()
            print("\nError output:")
            print(stderr.decode())
            input("Press Enter to exit...")
            sys.exit(1)
        
        print("✅ Server started successfully!")
        print("\n🌐 Opening browser...")
        
        # Open browser
        webbrowser.open('http://localhost:5000')
        
        print("\n" + "="*50)
        print("✨ Spotify Display is now running!")
        print("="*50)
        print("\n📌 The display should open in your browser")
        print("🔒 Keep this window open while using the app")
        print("❌ Close this window to stop the app")
        print("\n" + "="*50)
        
        # Keep the script running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down...")
            process.terminate()
            process.wait()
            print("✅ Stopped successfully")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()