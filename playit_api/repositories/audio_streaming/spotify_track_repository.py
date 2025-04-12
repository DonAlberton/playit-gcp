from models.track import Track
import json
import requests
from urllib.parse import quote
from requests.exceptions import HTTPError
from config import spotify_config


class SpotifyTrackRepository:
    api_url: str = spotify_config.api_url
    headers: str

    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}


    def get_user_name(self, user_id: str) -> str:
        try:
            response = requests.get(
                f"{self.api_url}/users/{quote(quote(user_id))}", 
                headers=self.headers
            )
            response.raise_for_status()

            data = response.json()

            return data["display_name"]
        
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")


    def get_added_tracks(self, playlist_id: str) -> list[Track]:
        try:
            response = requests.get(
                f"{self.api_url}/playlists/{playlist_id}", 
                headers=self.headers
            )
            response.raise_for_status()
        
            data = response.json()

            tracks: list[Track] = []

            for track in data["tracks"]["items"]:
                track_id: str = track["track"]["id"]

                user_url: str = track["added_by"]["external_urls"]["spotify"]

                user_id: str = ""
                i = len(user_url) - 1
            
                while user_url[i] != "/":
                    user_id = user_url[i] + user_id
                    i -= 1

                tracks.append(Track(track_id, user_id))

            return tracks
        
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")


    def delete_tracks(self, playlist_id: str, tracks_ids: list[str]) -> None:
        data: dict = {
            "tracks": [
                {
                    "uri": f"spotify:track:{track_id}",
                } for track_id in tracks_ids
            ]
        }

        try:
            response = requests.delete(
                f"{self.api_url}/playlists/{playlist_id}/tracks", 
                headers=self.headers, 
                data=json.dumps(data)
            )
            response.raise_for_status()

        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")

        
    def update_token(self, token) -> None:
        self.headers["Authorization"] = f"Bearer {token}"
