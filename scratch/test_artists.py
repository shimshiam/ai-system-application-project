import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

os.environ["SPOTIPY_CLIENT_ID"] = "72ecae9eae00436f99b083a423599598"
os.environ["SPOTIPY_CLIENT_SECRET"] = "b9f690a56f78486a98a22e27ca5d424f"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:8501"

auth = SpotifyOAuth(
    client_id=os.environ["SPOTIPY_CLIENT_ID"],
    client_secret=os.environ["SPOTIPY_CLIENT_SECRET"],
    redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
    scope="user-top-read",
    open_browser=False,
)

# Use client credentials flow just to test artists endpoint
from spotipy.oauth2 import SpotifyClientCredentials
client_creds = SpotifyClientCredentials(
    client_id=os.environ["SPOTIPY_CLIENT_ID"],
    client_secret=os.environ["SPOTIPY_CLIENT_SECRET"]
)
sp = spotipy.Spotify(auth_manager=client_creds)

try:
    artists = sp.artists(["1qjqW6fIrbWKKejfol8SkE"])
    print("SUCCESS:", len(artists["artists"]))
except Exception as e:
    print("ERROR:", e)

