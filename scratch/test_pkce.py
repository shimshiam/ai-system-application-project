import os
import spotipy
from spotipy.oauth2 import SpotifyPKCE
import json
import logging
logging.basicConfig(level=logging.DEBUG)
import requests
import urllib.parse

# Set fake client id
os.environ["SPOTIPY_CLIENT_ID"] = "72ecae9eae00436f99b083a423599598"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:8501"

auth = SpotifyPKCE(
    client_id=os.environ["SPOTIPY_CLIENT_ID"],
    redirect_uri=os.environ["SPOTIPY_REDIRECT_URI"],
    scope="user-top-read user-read-recently-played",
    open_browser=False,
)

url = auth.get_authorize_url(state="test-state-123")
print("AUTHORIZE URL:", url)
print("CODE VERIFIER:", auth.code_verifier)
print("CODE CHALLENGE:", auth.code_challenge)

