import base64
from dotenv import load_dotenv, set_key 
import os
from pathlib import Path
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout
from config import spotify_config

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

load_dotenv()

client_id = spotify_config.client_id # os.getenv("CLIENT_ID")
client_secret = spotify_config.client_secret # os.getenv("CLIENT_SECRET")
refresh_token = spotify_config.refresh_token # os.getenv("SPOTIFY_REFRESH_TOKEN")

url = "https://accounts.spotify.com/api/token"

auth_string = f"{client_id}:{client_secret}"
encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

data = {
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Authorization": f"Basic {encoded_auth}"
}

def token_refresh():
    try:
        response = requests.post(
            url, 
            headers=headers, 
            data=data
        )

        response.raise_for_status()
        
        response_data = response.json()

        return response_data["access_token"]

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")
    except ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
