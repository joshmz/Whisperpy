from dotenv import load_dotenv
import os
import sys
import contextlib
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Authenticate with Client Credentials Flow
client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
sp = Spotify(client_credentials_manager=client_credentials_manager)

@contextlib.contextmanager
def suppress_stderr():
    """Context manager to suppress stderr (for Spotipy noisy prints)."""
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

def get_playlist_tracks(playlist_url: str):
    """Fetch all tracks from a Spotify playlist (public only)."""
    try:
        playlist_id = playlist_url.split("playlist/")[1].split("?")[0]
    except IndexError:
        return []

    tracks = []
    try:
        with suppress_stderr():  # hide Spotipy's HTTP error noise
            results = sp.playlist_items(playlist_id, additional_types=["track"], limit=100)
    except SpotifyException:
        return []

    while results:
        for item in results["items"]:
            track = item.get("track")
            if track:
                name = track.get("name", "Unknown")
                artists = ", ".join([a["name"] for a in track.get("artists", [])])
                tracks.append(f"{name} - {artists}")

        if results["next"]:
            try:
                with suppress_stderr():
                    results = sp.next(results)
            except SpotifyException:
                return tracks
        else:
            results = None

    return tracks

def fetchSongs(plURL):
    songs = get_playlist_tracks(plURL)
    tracks = []
    if songs:
        # print(f"\n✅ Found {len(songs)} tracks:\n")
        for i, song in enumerate(songs, start=1):
            tracks.append(song)
    else:
        print("⚠️ No tracks found (maybe the playlist is private?).")
    return tracks