import os
import requests
from dotenv import load_dotenv
from requests.exceptions import HTTPError, ConnectionError, Timeout

load_dotenv()

token = os.getenv("SPOTIFY_ACCESS_TOKEN")
input_playlist_id = "5w7pHgT0XZ4jU69Rq1wPPu"

class SpotifyClient:
    api_url: str = os.getenv("SPOTIFY_API_URL")
    headers: str

    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_added_tracks(self, playlist_id: str):

        try:
            response = requests.get(f"{self.api_url}/playlists/{playlist_id}", headers=self.headers)
            response.raise_for_status()
            
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")
        except ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except Timeout as timeout_err:
            print(f"Request timed out: {timeout_err}")
        except Exception as err:
            print(f"An error occurred: {err}")

        if response.status_code != 200:
            return response.status_code

        data = response.json()

        return data
    
spotify_client = SpotifyClient(token)

spotify_client.get_added_tracks(input_playlist_id)
