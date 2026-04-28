import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8501")
if not client_id or not client_secret:
    raise RuntimeError("Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET before running this script.")

auth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope="user-top-read",
    open_browser=False,
)

# Use client credentials flow just to test artists endpoint
from spotipy.oauth2 import SpotifyClientCredentials
client_creds = SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)
sp = spotipy.Spotify(auth_manager=client_creds)

try:
    artists = sp.artists(["1qjqW6fIrbWKKejfol8SkE"])
    print("SUCCESS:", len(artists["artists"]))
except Exception as e:
    print("ERROR:", e)
