from typing import Generator
from models.track import Track
import os
import json
import requests
from dotenv import load_dotenv
from urllib.parse import quote

from config import spotify_config

# load_dotenv()

class TrackRepository:
    api_url: str = spotify_config.api_url # os.getenv("SPOTIFY_API_URL")
    headers: str

    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}
    

    def get_user_name(self, user_id: str) -> str:
        response = requests.get(
            f"{self.api_url}/users/{quote(quote(user_id))}", 
            headers=self.headers
        )

        assert response.status_code == 200
                
        data = response.json()

        return data["display_name"]
    

    # TODO: Change it to return a list of Tracks
    def get_added_tracks(self, playlist_id: str) -> list[Track]:
        response = requests.get(
            f"{self.api_url}/playlists/{playlist_id}", 
            headers=self.headers
        )

        assert response.status_code == 200
    
        data = response.json()

        tracks: list[Track] = []

        for track in data["tracks"]["items"]:
            track_id: str = track["track"]["id"]
            # track_name: str = track["track"]["name"]

            user_url: str = track["added_by"]["external_urls"]["spotify"]

            user_id: str = ""
            i = len(user_url) - 1
        
            while user_url[i] != "/":
                user_id = user_url[i] + user_id
                i -= 1

            tracks.append(Track(track_id, user_id))

        return tracks
            # yield Track(track_id, user_id)


    def delete_tracks(self, playlist_id: str, tracks_ids: list[str]) -> None:
        data: dict = {
            "tracks": [
                {
                    "uri": f"spotify:track:{track_id}",
                } for track_id in tracks_ids
            ]
        }

        response = requests.delete(f"{self.api_url}/playlists/{playlist_id}/tracks", headers=self.headers, data=json.dumps(data))

        assert response.status_code == 200

        
    def update_token(self, token) -> None:
        self.headers["Authorization"] = f"Bearer {token}"
