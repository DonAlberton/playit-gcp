import requests
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
from dotenv import load_dotenv
import os
from config import spotify_config

load_dotenv()

# Spotify client details
api_url = spotify_config.authentication_url # os.getenv("SPOTIFY_AUTHENTICATION_URL")
client_id = spotify_config.client_id # os.getenv("CLIENT_ID")
redirect_uri = spotify_config.redirect_url # os.getenv("REDIRECT_URL")
scope = 'playlist-modify-private playlist-modify-public'

def generate_random_string(length: int):
    import secrets
    import string
    possible = string.ascii_letters + string.digits
    return ''.join(secrets.choice(possible) for _ in range(length))

def sha256(plain: str):
    import hashlib
    data = plain.encode('utf-8')
    hash_object = hashlib.sha256(data).digest()
    return hash_object

def base64encode(input_bytes: str):
    import base64
    encoded = base64.urlsafe_b64encode(input_bytes).decode('utf-8').rstrip('=')
    return encoded

# Generate the code verifier and code challenge
code_verifier = generate_random_string(64)
hashed = sha256(code_verifier)
code_challenge = base64encode(hashed)

if not os.path.exists("verification"):
    os.makedirs("verification")

# Store code verifier in a file (simulating localStorage)
with open('verification/code_verifier.txt', 'w') as f:
    f.write(code_verifier)

# Prepare authorization URL
auth_url = "https://accounts.spotify.com/authorize"
params = {
    'response_type': 'code',
    'client_id': client_id,
    'scope': scope,
    'code_challenge_method': 'S256',
    'code_challenge': code_challenge,
    'redirect_uri': redirect_uri,
}

# Generate the complete URL with query parameters
auth_request = requests.Request('GET', auth_url, params=params).prepare()
auth_url_full = auth_request.url

# Open the URL in the default web browser
webbrowser.open(auth_url_full)

# HTTP server to handle the redirect request and capture the authorization code
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
    def fetch_token(code: str):
        # Load the code verifier from the file (simulating localStorage)
        with open('verification/code_verifier.txt', 'r') as f:
            code_verifier = f.read().strip()

        # Prepare the  payload for the POST request
        payload = {
            'client_id': client_id,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'code_verifier': code_verifier,
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        # Send the POST request to get the token
        response = requests.post(api_url, data=payload, headers=headers)

        # Parse the JSON response
        response_data = response.json()

        # Store the access token in a file (simulating localStorage)
        with open('verification/access_token.txt', 'w') as f:
            f.write(response_data['access_token'])

    # Use the captured authorization code to get the token
    fetch_token(authorization_code)
else:
    print("Authorization code was not received.")

def get_token():
    with open("verification/access_token.txt", "r") as file:
        access_token = file.readline()

    return access_token
