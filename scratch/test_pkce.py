import os
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import json
import logging
logging.basicConfig(level=logging.DEBUG)
import requests
import urllib.parse

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

url = auth.get_authorize_url(state="test-state-123")
print("AUTHORIZE URL:", url)
print("CODE VERIFIER:", auth.code_verifier)
print("CODE CHALLENGE:", auth.code_challenge)
