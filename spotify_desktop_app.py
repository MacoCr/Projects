import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template_string, jsonify
import time
import os
from dotenv import load_dotenv
import webview
import threading

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Spotify API credentials from .env file
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI', 'http://127.0.0.1:8888/callback')

# Scopes needed for playback control
SCOPE = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

# Validate environment variables
if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
    print("\nERROR: Missing Spotify credentials!")
    print("Please create a .env file with:")
    print("SPOTIPY_CLIENT_ID=your_client_id")
    print("SPOTIPY_CLIENT_SECRET=your_client_secret")
    print("SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback")
    exit(1)

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SCOPE
))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify Display</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { margin: 0; padding: 0; overflow-y: auto; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .animate-pulse { animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite; }
    </style>
</head>
<body class="bg-gradient-to-br from-purple-900 via-black to-blue-900 min-h-screen">
    <div class="flex items-center justify-center min-h-screen p-8">
        <div class="w-full max-w-4xl" id="app">
            <!-- Connection Status -->
            <div class="flex items-center justify-between mb-8">
                <div class="flex items-center gap-3">
                    <div id="status-dot" class="w-3 h-3 rounded-full bg-red-500 animate-pulse"></div>
                    <span class="text-white text-sm" id="status-text">Connecting...</span>
                </div>
                <svg class="text-white opacity-60" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                </svg>
            </div>

            <!-- Album Art -->
            <div class="relative mb-8">
                <div class="aspect-square w-full rounded-3xl overflow-hidden shadow-2xl bg-gray-800">
                    <img id="album-art" src="" alt="Album Art" class="w-full h-full object-cover">
                </div>
            </div>

            <!-- Track Info -->
            <div class="text-center mb-8">
                <h1 id="track-name" class="text-white text-4xl font-bold mb-3 truncate">No Track Playing</h1>
                <p id="artist-name" class="text-gray-300 text-2xl truncate">-</p>
                <p id="album-name" class="text-gray-400 text-lg mt-2 truncate">-</p>
            </div>

            <!-- Progress Bar -->
            <div class="mb-8">
                <div class="relative w-full h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div id="progress-bar" class="absolute left-0 top-0 h-full bg-gradient-to-r from-green-400 to-green-600" style="width: 0%"></div>
                </div>
                <div class="flex justify-between mt-2 text-gray-400 text-sm">
                    <span id="current-time">0:00</span>
                    <span id="total-time">0:00</span>
                </div>
            </div>

            <!-- Playback Controls -->
            <div class="flex items-center justify-center gap-8">
                <button onclick="previousTrack()" class="text-white hover:text-green-400 transition-colors p-4 hover:bg-white/10 rounded-full">
                    <svg width="36" height="36" viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="19 20 9 12 19 4 19 20"></polygon>
                        <polygon points="7 19 7 5 5 5 5 19 7 19"></polygon>
                    </svg>
                </button>
                
                <button onclick="togglePlayPause()" class="bg-white text-black hover:scale-105 transition-transform p-6 rounded-full shadow-lg">
                    <svg id="play-icon" width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                </button>
                
                <button onclick="nextTrack()" class="text-white hover:text-green-400 transition-colors p-4 hover:bg-white/10 rounded-full">
                    <svg width="36" height="36" viewBox="0 0 24 24" fill="currentColor">
                        <polygon points="5 4 15 12 5 20 5 4"></polygon>
                        <polygon points="19 5 19 19 17 19 17 5 19 5"></polygon>
                    </svg>
                </button>
            </div>
        </div>
    </div>

    <script>
        let isPlaying = false;

        function formatTime(ms) {
            const minutes = Math.floor(ms / 60000);
            const seconds = Math.floor((ms % 60000) / 1000);
            return minutes + ':' + seconds.toString().padStart(2, '0');
        }

        function updatePlayIcon(playing) {
            const icon = document.getElementById('play-icon');
            if (playing) {
                icon.innerHTML = '<rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect>';
            } else {
                icon.innerHTML = '<polygon points="5 3 19 12 5 21 5 3"></polygon>';
            }
        }

        async function updateCurrentTrack() {
            try {
                const response = await fetch('/current-track');
                const data = await response.json();
                
                if (data.playing !== false && data.name) {
                    document.getElementById('status-dot').className = 'w-3 h-3 rounded-full bg-green-500 animate-pulse';
                    document.getElementById('status-text').textContent = 'Connected to Spotify';
                    
                    document.getElementById('track-name').textContent = data.name;
                    document.getElementById('artist-name').textContent = data.artist;
                    document.getElementById('album-name').textContent = data.album;
                    document.getElementById('album-art').src = data.albumArt;
                    
                    const progress = (data.progress / data.duration) * 100;
                    document.getElementById('progress-bar').style.width = progress + '%';
                    document.getElementById('current-time').textContent = formatTime(data.progress);
                    document.getElementById('total-time').textContent = formatTime(data.duration);
                    
                    isPlaying = data.playing;
                    updatePlayIcon(isPlaying);
                } else {
                    document.getElementById('status-dot').className = 'w-3 h-3 rounded-full bg-yellow-500 animate-pulse';
                    document.getElementById('status-text').textContent = 'No track playing';
                }
            } catch (error) {
                console.error('Error fetching track:', error);
                document.getElementById('status-dot').className = 'w-3 h-3 rounded-full bg-red-500 animate-pulse';
                document.getElementById('status-text').textContent = 'Connection error';
            }
        }

        async function togglePlayPause() {
            try {
                const endpoint = isPlaying ? '/pause' : '/play';
                const response = await fetch(endpoint, { method: 'POST' });
                const data = await response.json();
                
                if (data.error) {
                    console.error('Playback error:', data.error);
                    alert('Error: ' + data.error);
                } else {
                    // Immediately toggle the icon for better responsiveness
                    isPlaying = !isPlaying;
                    updatePlayIcon(isPlaying);
                    // Then update from server after a moment
                    setTimeout(updateCurrentTrack, 300);
                }
            } catch (error) {
                console.error('Error toggling playback:', error);
                alert('Connection error - check console');
            }
        }

        async function nextTrack() {
            try {
                await fetch('/next', { method: 'POST' });
                setTimeout(updateCurrentTrack, 500);
            } catch (error) {
                console.error('Error skipping track:', error);
            }
        }

        async function previousTrack() {
            try {
                await fetch('/previous', { method: 'POST' });
                setTimeout(updateCurrentTrack, 500);
            } catch (error) {
                console.error('Error going to previous track:', error);
            }
        }

        // Update every second
        updateCurrentTrack();
        setInterval(updateCurrentTrack, 1000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/current-track')
def get_current_track():
    """Get currently playing track"""
    try:
        current = sp.current_playback()
        
        if current is None or current.get('item') is None:
            return jsonify({'playing': False})
        
        track = current['item']
        
        return jsonify({
            'playing': current['is_playing'],
            'name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'albumArt': track['album']['images'][0]['url'] if track['album']['images'] else '',
            'duration': track['duration_ms'],
            'progress': current['progress_ms'],
            'uri': track['uri']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/play', methods=['POST'])
def play():
    """Resume playback"""
    try:
        # Get available devices
        devices = sp.devices()
        if not devices or not devices.get('devices'):
            return jsonify({'error': 'No devices available'}), 404
        
        # Find an active device or use the first available one
        device_id = None
        for device in devices['devices']:
            if device['is_active']:
                device_id = device['id']
                break
        
        if not device_id and devices['devices']:
            device_id = devices['devices'][0]['id']
        
        # Start playback on the device
        sp.start_playback(device_id=device_id)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Play error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/pause', methods=['POST'])
def pause():
    """Pause playback"""
    try:
        # Get available devices
        devices = sp.devices()
        if not devices or not devices.get('devices'):
            return jsonify({'error': 'No devices available'}), 404
        
        # Find an active device
        device_id = None
        for device in devices['devices']:
            if device['is_active']:
                device_id = device['id']
                break
        
        if device_id:
            sp.pause_playback(device_id=device_id)
        else:
            sp.pause_playback()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Pause error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/next', methods=['POST'])
def next_track():
    """Skip to next track"""
    try:
        sp.next_track()
        time.sleep(0.3)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/previous', methods=['POST'])
def previous_track():
    """Skip to previous track"""
    try:
        sp.previous_track()
        time.sleep(0.3)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def start_flask():
    """Start Flask server in a separate thread"""
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("=" * 50)
    print("Spotify Desktop App Starting...")
    print("=" * 50)
    print(f"\nLoaded credentials from .env file")
    print(f"Client ID: {SPOTIPY_CLIENT_ID[:10]}...")
    print(f"Redirect URI: {SPOTIPY_REDIRECT_URI}")
    print("\nStarting desktop application...")
    print("=" * 50 + "\n")
    
    # Start Flask in a background thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Give Flask a moment to start
    time.sleep(2)
    
    # Check if icon exists
    import sys
    from pathlib import Path
    
    icon_path = None
    script_dir = Path(__file__).parent
    
    # Look for icon files
    for ext in ['.ico', '.png', '.icns']:
        potential_icon = script_dir / f'spotify_icon{ext}'
        if potential_icon.exists():
            icon_path = str(potential_icon)
            print(f"Found icon: {icon_path}")
            break
    
    if not icon_path:
        print("No icon found. Add 'spotify_icon.ico' or 'spotify_icon.png' for a custom icon.")
    
    # Create and show the desktop window
    window = webview.create_window(
        'Spotify Display',
        'http://127.0.0.1:5000',
        width=1200,
        height=900,
        resizable=True,
        frameless=False
    )
    
    webview.start()