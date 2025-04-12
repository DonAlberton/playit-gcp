from fastapi import FastAPI, Body
import uvicorn
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout
import json
from users_priorities import UsersPriorities

import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(".") / ".env"

load_dotenv(dotenv_path=env_path)

PLAYIT_URL_BASE = os.getenv("PLAYIT_URL_BASE")
CLASSIFIER_URL_BASE = os.getenv("CLASSIFIER_URL_BASE")
SCHEDULER_URL_BASE = os.getenv("SCHEDULER_URL_BASE") 

app = FastAPI()

headers = { "Content-Type": "application/json" }

@app.get("/test")
def test():
    return "test"

@app.post("/create-session")
def create_session(input_playlist_name: str = Body(...)):
        
    playlists = {}

    data = {
        "name": input_playlist_name,
        "is_public": True
    }

    try:
        response = requests.post(f"{PLAYIT_URL_BASE}/playlists", headers=headers, data=json.dumps(data))        
        response.raise_for_status()

        response_json = json.loads(response.content)

        playlists.update({"input_playlist_id": response_json["playlist_id"]})
        
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")
    except ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    try:
        data.update({"name": f"{input_playlist_name}-output"})
        data.update({"is_public": False})
        
        response = requests.post(
            f"{PLAYIT_URL_BASE}/playlists", 
            headers=headers, 
            data=json.dumps(data)
        )

        response.raise_for_status()

        response_json = json.loads(response.content)

        playlists.update({"output_playlist_id": response_json["playlist_id"]})
        
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")
    except ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    
    set_playlists(playlists["input_playlist_id"], playlists["output_playlist_id"])

    return playlists

# TODO: Remove it
@app.post("/set-playlists")
def set_playlists(input_playlist: str, output_playlist: str):
    data = { "input_playlist": input_playlist }

    # Change it to send the data
    response = requests.post(f"{CLASSIFIER_URL_BASE}/playlists", headers=headers, data=json.dumps(input_playlist))

    # Change it to send the data
    data = { "output_playlist": output_playlist }
    response = requests.post(f"{SCHEDULER_URL_BASE}/playlists", headers=headers, data=json.dumps(output_playlist))

@app.post("/set-priorities")
def set_priorities(low: int = Body(...), medium: int = Body(...), high: int = Body(...)):
    data = {
        "low": low,
        "medium": medium,
        "high": high
    }

    response = requests.post(f"{SCHEDULER_URL_BASE}/priorities", headers=headers, data=json.dumps(data))

@app.post("/set-users-priorities")
def set_users_priorities(users_priorities: UsersPriorities):
    response = requests.put(f"{CLASSIFIER_URL_BASE}/priorities", headers=headers, data=json.dumps(users_priorities.model_dump()))

@app.post("/get-users")
def get_users(input_playlist_id: str = Body(...)):
    try:
        response = requests.get(f"{PLAYIT_URL_BASE}/playlists/{input_playlist_id}/users", headers=headers)
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")
    except ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

    return json.loads(response.content)

@app.post("/start-session")
def start_session():
    response = requests.post(f"{CLASSIFIER_URL_BASE}/start", headers=headers)

    response = requests.post(f"{SCHEDULER_URL_BASE}/start", headers=headers)

@app.post("/stop-session")
def stop_session():
    response = requests.post(f"{CLASSIFIER_URL_BASE}/stop", headers=headers)

    response = requests.post(f"{SCHEDULER_URL_BASE}/stop", headers=headers)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)