import os
import requests
from spotipy.oauth2 import SpotifyClientCredentials

os.environ["SPOTIPY_CLIENT_ID"] = "72ecae9eae00436f99b083a423599598"
os.environ["SPOTIPY_CLIENT_SECRET"] = "b9f690a56f78486a98a22e27ca5d424f"

cc = SpotifyClientCredentials(
    client_id=os.environ["SPOTIPY_CLIENT_ID"],
    client_secret=os.environ["SPOTIPY_CLIENT_SECRET"]
)
token = cc.get_access_token(as_dict=False)

res = requests.get(
    "https://api.spotify.com/v1/artists?ids=1qjqW6fIrbWKKejfol8SkE",
    headers={"Authorization": f"Bearer {token}"}
)
print("STATUS WITHOUT SLASH:", res.status_code)
print("BODY WITHOUT SLASH:", res.text)
