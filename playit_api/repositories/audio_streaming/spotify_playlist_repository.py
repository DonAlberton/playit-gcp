from models.playlist import Playlist
from config import spotify_config
import json
import requests


class SpotifyPlaylistRepository:
    api_url: str = spotify_config.api_url
    headers: str

    def __init__(self, token: str):        
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"            
        }


    def create_playlist(self, playlist_name: str, user_id: str, is_public: bool) -> Playlist:
        data: dict = {
            "name": playlist_name,
            "description": "",
            "collaborative": True,
            "public": is_public
        }
    
        response = requests.post(
            f"{self.api_url}/users/{user_id}/playlists",
            headers=self.headers,
            data=json.dumps(data)
        )

        assert response.status_code == 201

        json_response = response.json()

        playlist_id: str = json_response["id"]

        return Playlist(playlist_id=playlist_id, name=playlist_name)


    def unfollow_playlist(self, playlist_id: str) -> None:
        response = requests.delete(
            f"{self.api_url}/playlists/{playlist_id}/followers", 
            headers=self.headers
        )

        assert response.status_code == 200


    def add_track(self, playlist_id: str, track_id: str) -> None:
        data: dict = {
            "uris":[
                f"spotify:track:{track_id}"
            ]
        }

        response = requests.post(
            f"{self.api_url}/playlists/{playlist_id}/tracks", 
            headers=self.headers, 
            data=json.dumps(data)
        )

        assert response.status_code == 201


    def add_tracks(self, playlist_id: str, tracks: list[str]) -> None:
        data = {
            "uris":[
                f"spotify:track:{track}" for track in tracks
            ]
        }

        response = requests.post(
            f"{self.api_url}/playlists/{playlist_id}/tracks",
            headers=self.headers,
            data=json.dumps(data)
        )

        assert response.status_code == 201
    

    def update_token(self, token):
        self.headers["Authorization"] = f"Bearer {token}"
