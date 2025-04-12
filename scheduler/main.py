from fastapi import FastAPI, Body
from models import QueueWeights, StartSchedulerRequest
import requests
from requests.exceptions import HTTPError
import json
from gcp import *

app = FastAPI()

PLAYIT_URL_BASE = "http://127.0.0.1:8000"
firestore_client: FirestoreClient = FirestoreClient()
subsciber: PubsubSubscriberClient = PubsubSubscriberClient()

# TODO: Change POST to PUT on App Gateway
# TODO: Change /priority to /weights on App Gateway
@app.put("/weights/{input_playlist_id}")
async def update_queue_weights(input_playlist_id: str, queue_weights: QueueWeights) -> None:
    firestore_client.update_queue_weights(input_playlist_id, queue_weights)
    

@app.post("/start/{input_playlist_id}")
async def start_scheduler(input_playlist_id: str, output_playlist_id: StartSchedulerRequest) -> None:
    print(output_playlist_id)
    queue_weights: QueueWeights = firestore_client.get_queue_weights(input_playlist_id)
    output_tracks_ids: list[str] = subsciber.pull_tracks(input_playlist_id, queue_weights)
    push_api(output_playlist_id, output_tracks_ids)


def push_api(playlist_id: str, tracks_ids: list[str]) -> None:
    print(tracks_ids)
    if not tracks_ids:
        return  

    try:
        headers = { "Content-Type": "application/json" }
        response = requests.post(f"{PLAYIT_URL_BASE}/playlists/{playlist_id}/tracks", 
            headers=headers, 
            data=json.dumps(tracks_ids)
        )        
        response.raise_for_status()
    
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")


# TODO: Change sync redis to async
def pull_redis():
    return 
    with rd.pipeline() as pipe:
        for priority, value in priorities.items():
            # pipe.lrange(priority, 0, value-1)
            # pipe.ltrim(priority, value, -1)
            for _ in range(value):
                pipe.lpop(priority)

        output_playlist = pipe.execute()

    return [byte.decode('utf-8') for byte in output_playlist if byte]
