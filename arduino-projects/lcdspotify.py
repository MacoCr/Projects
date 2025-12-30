import spotipy
from spotipy.oauth2 import SpotifyOAuth
import serial
import time

# Spotify API credentials
SPOTIPY_CLIENT_ID = '64d6226627604f05af4d80a4473eb95b'
SPOTIPY_CLIENT_SECRET = '269dffbe652d4159870f1b62784b88f8'
SPOTIPY_REDIRECT_URI = 'https://127.0.0.1:8888/callback'

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope='user-read-currently-playing'
))

# Initialize serial connection (adjust COM port for your system)
arduino = serial.Serial('COM3', 9600, timeout=1)  # Use '/dev/ttyUSB0' or similar on Linux/Mac
time.sleep(2)  # Wait for Arduino to reset

previous_track = None
try:
    while True:
        try:
            current = sp.current_user_playing_track()
        
            if current and current['is_playing']:
                track_name = current['item']['name']
                artist_name = current['item']['artists'][0]['name']
            
                current_track = f"{track_name} - {artist_name}"
            
            # Only send if track changed
                if current_track != previous_track:
                # Send to Arduino (truncate if too long for LCD)
                    message = f"{track_name[:16]}|{artist_name[:16]}\n"
                    arduino.write(message.encode())
                    print(f"Sent: {current_track}")
                    previous_track = current_track
            else:
                if previous_track != "Nothing playing":
                    arduino.write("Nothing playing|\n".encode())
                    previous_track = "Nothing playing"
                
        except Exception as e:
            print(f"Error: {e}")

        time.sleep(2)  # Check every 2 seconds
except KeyboardInterrupt:
    print("Exiting...")
