import os
import requests
from spotipy.oauth2 import SpotifyClientCredentials

client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
if not client_id or not client_secret:
    raise RuntimeError("Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET before running this script.")

cc = SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)
token = cc.get_access_token(as_dict=False)

res = requests.get(
    "https://api.spotify.com/v1/artists?ids=1qjqW6fIrbWKKejfol8SkE",
    headers={"Authorization": f"Bearer {token}"}
)
print("STATUS WITHOUT SLASH:", res.status_code)
print("BODY WITHOUT SLASH:", res.text)
