import requests
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
import string
import random
from dotenv import load_dotenv, set_key
from pathlib import Path
import os
import base64
from config import spotify_config


# Spotify client details
api_url = spotify_config.api_url # os.getenv("SPOTIFY_AUTHENTICATION_URL")
client_id = spotify_config.client_id # os.getenv("CLIENT_ID")
redirect_uri = spotify_config.redirect_url # os.getenv("REDIRECT_URL")
client_secret = spotify_config.client_secret # os.getenv("CLIENT_SECRET")
auth_url = "https://accounts.spotify.com/authorize"

scope = 'playlist-modify-private playlist-modify-public'

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

state = generate_random_string(16)

params = {
    'response_type': 'code',
    'client_id': client_id,
    'scope': scope,
    'redirect_uri': redirect_uri,
    'state': state
}


auth_request = requests.Request('GET', auth_url, params=params).prepare()
auth_url_full = auth_request.url
webbrowser.open(auth_url_full)

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        code = query_components.get('code', [None])[0]
        if code:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Authorization successful. You can close this window.')
            global authorization_code
            authorization_code = code
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Authorization failed.')

authorization_code = None

server_address = ('', 8888)
httpd = HTTPServer(server_address, RedirectHandler)
print('Waiting for authorization code...')
httpd.handle_request()

if authorization_code:
    payload = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri
    }

    auth_string = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')


    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f"Basic {encoded_auth}"
    }

    response = requests.post(api_url, data=payload, headers=headers)

    response_data = response.json()

    # set_key(dotenv_path=env_path, key_to_set="SPOTIFY_ACCESS_TOKEN", value_to_set=response_data['access_token'])
    # set_key(dotenv_path=env_path, key_to_set="SPOTIFY_REFRESH_TOKEN", value_to_set=response_data['refresh_token'])

else:
    print("Authorization code was not received.")
