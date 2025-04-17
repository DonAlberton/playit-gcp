from models.playlist import Playlist
from config import spotify_config
import json
import requests
from requests.exceptions import HTTPError

class SpotifyPlaylistRepository:
    api_url: str = spotify_config.api_url
    headers: str
    user_id: str = spotify_config.user_id #"11180277231"

    def __init__(self, token: str):        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"            
        }


    def create_playlist(self, playlist_name: str, is_public: bool = True) -> Playlist:
        data: dict = {
            "name": playlist_name,
            "description": "",
            "collaborative": True,
            "public": is_public
        }

        try:    
            response = requests.post(
                f"{self.api_url}/users/{self.user_id}/playlists",
                headers=self.headers,
                data=json.dumps(data)
            )

            json_response = response.json()

            playlist_id: str = json_response["id"]

            return Playlist(playlist_id=playlist_id, name=playlist_name)
        
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")


    def unfollow_playlist(self, playlist_id: str) -> None:
        try:
            response = requests.delete(
                f"{self.api_url}/playlists/{playlist_id}/followers", 
                headers=self.headers
            )

        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")
        


    def add_track(self, playlist_id: str, track_id: str) -> None:
        data: dict = {
            "uris":[
                f"spotify:track:{track_id}"
            ]
        }

        try:
            response = requests.post(
                f"{self.api_url}/playlists/{playlist_id}/tracks", 
                headers=self.headers, 
                data=json.dumps(data)
            )

        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")


    def add_tracks(self, playlist_id: str, tracks: list[str]) -> None:
        data = {
            "uris":[
                f"spotify:track:{track}" for track in tracks
            ]
        }

        try:
            response = requests.post(
                f"{self.api_url}/playlists/{playlist_id}/tracks",
                headers=self.headers,
                data=json.dumps(data)
            )
            response.raise_for_status()

        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")
    

    def update_token(self, token):
        self.headers["Authorization"] = f"Bearer {token}"
