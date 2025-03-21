from models.playlist import Playlist
from models.track import Track
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class PlaylistRepository:
    api_url: str = os.getenv("SPOTIFY_API_URL")
    headers: str

    def __init__(self, token):        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"            
        }

    def create_playlist(self, playlist_name, user_id: str):
        data = {
            "name": playlist_name,
            "description": "First playlist created using Spotify API",
            "collaborative": True,
            "public": True
        }
    
        response = requests.post(
            f"{self.api_url}/users/{user_id}/playlists",
            headers=self.headers,
            data=json.dumps(data)
        )

        assert response.status_code == 200

        json_response = response.json()

        playlist_id = json_response["id"]

        return Playlist(playlist_id=playlist_id, name=playlist_name)

    def unfollow_playlist(self, playlist_id: str):
        response = requests.delete(
            f"{self.api_url}/playlists/{playlist_id}/followers", 
            headers=self.headers
        )

        assert response.status_code == 200

    def add_track(self, playlist_id: str, track_id: str):
        data = {
            "uris":[
                f"spotify:track:{track_id}"
            ]
        }

        response = requests.post(
            f"{self.api_url}/playlists/{playlist_id}/tracks", 
            headers=self.headers, 
            data=json.dumps(data)
        )

        assert response.status_code == 200


    def add_tracks(self, playlist_id: str, tracks: list[str]):
        data = {
            "uris":[
                f"spotify:track:{track}" for track in tracks
            ]
        }

        reponse = requests.post(
            f"{self.api_url}/playlists/{playlist_id}/tracks",
            headers=self.headers,
            data=json.dumps(data)
        )

        assert reponse.status_code == 200
    
    def update_token(self, token):
        self.headers["Authorization"] = f"Bearer {token}"