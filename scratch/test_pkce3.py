import json
import os
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import requests

os.environ["SPOTIPY_CLIENT_ID"] = "72ecae9eae00436f99b083a423599598"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:8501"

auth2 = SpotifyPKCE(
    client_id=os.environ["SPOTIPY_CLIENT_ID"],
    redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
    scope="user-top-read user-read-recently-played",
    open_browser=False,
)
auth2.code_verifier = "wrong_verifier"

try:
    auth2.get_access_token("fake_code")
except Exception as e:
    print("EXPECTED ERROR:", e)

