from fastapi import FastAPI, Body
from models import QueueWeights, StartSchedulerRequest
import requests
from requests.exceptions import HTTPError
import json
from gcp import *
from config import playit_settings, gcp_settings
from fastapi.responses import JSONResponse


firestore_client: FirestoreClient = FirestoreClient()
subsciber: PubsubSubscriberClient = PubsubSubscriberClient(project_id=gcp_settings.project_id)
task_client: TasksClient = TasksClient(
    queue_id=gcp_settings.queue_id,
    location=gcp_settings.cloudtask_location,
    project_id=gcp_settings.project_id,
    retry_url=gcp_settings.scheduler_retry_url
)


app = FastAPI()

# TODO: Change POST to PUT on App Gateway
# TODO: Change /priority to /weights on App Gateway
@app.put("/weights/{input_playlist_id}")
async def update_queue_weights(input_playlist_id: str, queue_weights: QueueWeights) -> None:
    firestore_client.update_queue_weights(input_playlist_id, queue_weights)


@app.post("/start/{input_playlist_id}")
async def start_scheduler(input_playlist_id: str, start_scheduler_request: StartSchedulerRequest) -> None:
    if start_scheduler_request.trigger_mode == "manual":
        if not firestore_client.check_taskqueue_readiness(input_playlist_id):
            firestore_client.set_taskqueue_readiness(input_playlist_id, True)
            queue_weights: QueueWeights = firestore_client.get_queue_weights(input_playlist_id)
            output_tracks_ids: list[str] = subsciber.pull_tracks(input_playlist_id, queue_weights)
            push_api(start_scheduler_request.output_playlist_id, output_tracks_ids)
            start_scheduler_request.trigger_mode = "automatic"
            task_client.push_scheduler_reprocessing(input_playlist_id, start_scheduler_request.model_dump_json())

            return JSONResponse(
                status_code=201,
                content={"message": f"{input_playlist_id} processing started"}
            )

        return JSONResponse(
            status_code=409,
            content={"message": f"{input_playlist_id} is already processing"}
        )
    
    if not firestore_client.check_taskqueue_readiness(input_playlist_id):
        return JSONResponse(
            status_code=200,
            content={"message": f"{input_playlist_id} processing flag is set to false"}
        )

    queue_weights: QueueWeights = firestore_client.get_queue_weights(input_playlist_id)
    output_tracks_ids: list[str] = subsciber.pull_tracks(input_playlist_id, queue_weights)
    push_api(start_scheduler_request.output_playlist_id, output_tracks_ids)
    task_client.push_scheduler_reprocessing(input_playlist_id, start_scheduler_request.model_dump_json())
    
    return JSONResponse(
        status_code=200,
        content={"message": f"{input_playlist_id} processing"}
    )


@app.post("/stop/{input_playlist_id}")
def stop_scheduler(input_playlist_id: str):
    firestore_client.set_taskqueue_readiness(input_playlist_id, False)


def push_api(playlist_id: str, tracks_ids: list[str]) -> None:
    if not tracks_ids:
        return  

    try:
        headers = { "Content-Type": "application/json" }
        response = requests.post(f"{playit_settings.url}/playlists/{playlist_id}/tracks", 
            headers=headers, 
            data=json.dumps(tracks_ids)
        )        
        response.raise_for_status()
    
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")
    
