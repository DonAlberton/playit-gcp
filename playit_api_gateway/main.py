from fastapi import FastAPI, Body
import requests
from requests.exceptions import HTTPError
import json
from models import *
from gcp import *
from config import playit_settings

firestore_client = FirestoreClient()

app = FastAPI()

headers = { "Content-Type": "application/json" }

@app.post("/create-session")
def create_session(input_playlist_name: str = Body(...)):
        
    playlists_ids = {}

    data = {
        "name": input_playlist_name,
        "is_public": True
    }

    try:
        response = requests.post(f"{playit_settings.playit_url}/playlists", 
            headers=headers, 
            data=json.dumps(data)
        )        
        response.raise_for_status()

        response_json = response.json()
        playlists_ids["input_playlist_id"] = response_json["playlist_id"]
        
        
        data = {
            "name": f"{input_playlist_name}-output",
            "is_public": False
        }
        
        response = requests.post(
            f"{playit_settings.playit_url}/playlists", 
            headers=headers, 
            data=json.dumps(data)
        )
        response.raise_for_status()

        response_json = response.json()

        playlists_ids["output_playlist_id"] = response_json["playlist_id"]

        firestore_client.set_input_output_playlist(playlists_ids["input_playlist_id"], playlists_ids["output_playlist_id"])

        return playlists_ids
        
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")


@app.put("/set-queues-weights/{input_playlist_id}")
def set_queue_weights(input_playlist_id: str, set_queues_weights_request: SetQueuesWeightsRequest):
    try:
        response = requests.put(
            f"{playit_settings.scheduler_url}/weights/{input_playlist_id}", 
            headers=headers, 
            data=set_queues_weights_request.model_dump_json()
        )
        response.raise_for_status()

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")


@app.put("/set-users-priorities/{input_playlist_id}")
def set_users_priorities(input_playlist_id: str, set_users_priorities_request: SetUsersPrioritiesRequest):
    try:
        response = requests.put(
            f"{playit_settings.classifier_url}/priorities/{input_playlist_id}",
            headers=headers, 
            data=set_users_priorities_request.model_dump_json()
        )
        response.raise_for_status()

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")


@app.get("/users/{input_playlist_id}")
def get_users(input_playlist_id: str):
    try:
        response = requests.get(
            f"{playit_settings.playit_url}/playlists/{input_playlist_id}/users", 
            headers=headers
        )
        response.raise_for_status()

        return response.json()

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")


@app.post("/start-session/{input_playlist_id}")
def start_session(input_playlist_id: str):
    output_playlist_id: str = firestore_client.get_output_playlist_id(input_playlist_id)

    try:
        start_classifier_request = StartClassifierRequest(trigger_mode="manual")
        response = requests.post(
            f"{playit_settings.classifier_url}/start/{input_playlist_id}", 
            headers=headers,
            data=start_classifier_request.model_dump_json()
        )
        response.raise_for_status()

        start_scheduler_request = StartSchedulerRequest(trigger_mode="automatic", output_playlist_id=output_playlist_id)
        response = requests.post(
            f"{playit_settings.scheduler_url}/start/{input_playlist_id}", 
            headers=headers,
            data=start_scheduler_request.model_dump_json()
        )
        response.raise_for_status()

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")


@app.post("/stop-session/{input_playlist_id}")
def stop_session(input_playlist_id: str):
    try:
        response = requests.post(
            f"{playit_settings.classifier_url}/stop/{input_playlist_id}", 
            headers=headers,
        )
        response.raise_for_status()

        if response.status_code == 200:
            return

        response = requests.post(
            f"{playit_settings.scheduler_url}/stop/{input_playlist_id}", 
            headers=headers,
        )
        response.raise_for_status()

        return 

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")
