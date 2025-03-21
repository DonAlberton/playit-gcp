from models.track import Track
import os
import json
import requests
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

class TrackRepository:
    api_url: str = os.getenv("SPOTIFY_API_URL")
    headers: str

    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def get_user_name(self, user_id: str):
        r = requests.get(f"{self.api_url}/users/{quote(quote(user_id))}", headers=self.headers)
        # print(f"{self.api_url}/users/{urlparse(user_id)}")
        if r.status_code != 200:
            return r.status_code
                
        data = r.json()

        return data["display_name"]
    
    def get_added_tracks(self, playlist_id: str):
        r = requests.get(f"{self.api_url}/playlists/{playlist_id}", headers=self.headers)

        if r.status_code != 200:
            return r.status_code

        data = r.json()

        for track in data["tracks"]["items"]:
            track_id = track["track"]["id"]
            track_name = track["track"]["name"]

            user_url = track["added_by"]["external_urls"]["spotify"]

            user_id = ""
            i = len(user_url) - 1
        
            while user_url[i] != "/":
                user_id = user_url[i] + user_id
                i -= 1

            yield Track(track_id, user_id)

    def delete_tracks(self, playlist_id: str, tracks_ids: list[str]):
        data = {
            "tracks": [
                {
                    "uri": f"spotify:track:{track_id}",
                } for track_id in tracks_ids
            ]
        }

        r = requests.delete(f"{self.api_url}/playlists/{playlist_id}/tracks", headers=self.headers, data=json.dumps(data))

        
    def update_token(self, token):
        self.headers["Authorization"] = f"Bearer {token}"