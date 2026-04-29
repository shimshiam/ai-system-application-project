import json
import os
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import requests

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
print("VERIFIER:", auth.code_verifier)

# Simulate what streamlit does on reload
auth2 = SpotifyPKCE(
    client_id=client_id,
    redirect_uri=redirect_uri,
    scope="user-top-read user-read-recently-played",
    open_browser=False,
)
auth2.code_verifier = auth.code_verifier

# If we try to get access token with a fake code, it should fail with "Invalid authorization code", not "code_verifier was incorrect".
try:
    auth2.get_access_token("fake_code")
except Exception as e:
    print("EXPECTED ERROR:", e)
