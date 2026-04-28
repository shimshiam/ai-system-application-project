import os
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import requests

# Monkeypatch requests.post
original_post = requests.post

def intercept_post(url, *args, **kwargs):
    print("--- POST REQUEST INTERCEPTED ---")
    print("URL:", url)
    print("DATA:", kwargs.get("data"))
    print("--------------------------------")
    return original_post(url, *args, **kwargs)

requests.post = intercept_post
requests.Session.post = intercept_post

client_id = os.getenv("SPOTIPY_CLIENT_ID")
redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8501")
if not client_id:
    raise RuntimeError("Set SPOTIPY_CLIENT_ID before running this script.")

auth = SpotifyPKCE(
    client_id=client_id,
    redirect_uri=redirect_uri,
    scope="user-top-read user-read-recently-played",
    open_browser=False,
)

auth.code_verifier = "MY_TEST_VERIFIER_123"

try:
    auth.get_access_token("fake_code")
except Exception as e:
    print("ERROR:", e)
