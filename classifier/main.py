from fastapi import FastAPI
from fastapi.responses import JSONResponse
import requests
from requests.exceptions import HTTPError
import json

from gcp.cloud_tasks.tasks_client import TasksClient
from gcp.firestore.firestore_client import FirestoreClient
from gcp.pubsub.subscriber_client import PubsubSubscriberClient
from gcp.pubsub.publisher_client import PubsubPublisherClient
from models.users_by_priorities import UsersByPriorities
from models.priorities import Priorities
from models.start_classifier_request import StartClassifierRequest
from config import gcp_settings, playit_settings

firestore_client: FirestoreClient = FirestoreClient()
publisher: PubsubPublisherClient = PubsubPublisherClient(project_id=gcp_settings.project_id)
task_client: TasksClient = TasksClient(
    project_id=gcp_settings.project_id,
    location=gcp_settings.cloudtask_location,
    queue_id=gcp_settings.queue_id,
    retry_url=gcp_settings.classifier_retry_url
)


app = FastAPI()

@app.post("/start/{input_playlist_id}")
async def start_classifier(input_playlist_id: str, start_classifier_request: StartClassifierRequest) -> None:
    if start_classifier_request.trigger_mode == "manual":
        if not firestore_client.check_taskqueue_readiness(input_playlist_id):
            firestore_client.set_taskqueue_readiness(input_playlist_id, True)
            users_priorities: UsersByPriorities = firestore_client.get_users_priorities(input_playlist_id)
            tracks: dict = fetch_tracks(input_playlist_id)
            classified: Priorities = classify_tracks(tracks, users_priorities)
            publisher.push_queues_messages(input_playlist_id, classified)
            start_classifier_request.trigger_mode = "automatic"
            task_client.push_classifier_reprocessing(input_playlist_id, start_classifier_request.model_dump_json())
            
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
    
    users_priorities: UsersByPriorities = firestore_client.get_users_priorities(input_playlist_id)
    tracks: dict = fetch_tracks(input_playlist_id)
    classified: Priorities = classify_tracks(tracks, users_priorities)
    publisher.push_queues_messages(input_playlist_id, classified)
    task_client.push_classifier_reprocessing(input_playlist_id, start_classifier_request.model_dump_json())
    
    return JSONResponse(
        status_code=200,
        content={"message": f"{input_playlist_id} processing"}
    )


@app.put("/priorities/{input_playlist_id}")
def set_users_priorities(input_playlist_id: str, users_priorities: UsersByPriorities) -> None:
    
    if not firestore_client.does_playlist_exist(input_playlist_id):
        publisher.create_topics(input_playlist_id)
        subscriber: PubsubSubscriberClient = PubsubSubscriberClient()
        subscriber.create_subscriptions(input_playlist_id)

    firestore_client.update_users_priorities(input_playlist_id, users_priorities)


@app.post("/stop/{input_playlist_id}")
def stop_classifier(input_playlist_id: str):
    firestore_client.set_taskqueue_readiness(input_playlist_id, False)


def fetch_tracks(input_playlist_id: str) -> dict:
    try:
        response = requests.get(f"{playit_settings.url}/playlists/{input_playlist_id}/tracks")
        response.raise_for_status()

        data = json.loads(response.content)

        tracks_ids = [track_data["track_id"] for track_data in data]

        headers = { "Content-Type": "application/json" }
        response = requests.delete(
            f"{playit_settings.url}/playlists/{input_playlist_id}/tracks",
            headers=headers, 
            data=json.dumps(tracks_ids)
        )
        response.raise_for_status()

        return data

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")


def classify_tracks(tracks: dict, users_priorities: UsersByPriorities) -> Priorities:
    queues = Priorities()

    users_dict: dict = users_priorities.model_dump()
    
    tracks_with_no_priorities: list[str] = []

    for track in tracks:
        user_id = track["added_by_id"]
        track_id = track["track_id"]

        tracks_with_no_priorities.append(track_id)
        for priority, users_id in users_dict.items():
            if user_id in users_id:
                getattr(queues, priority).append(track_id)
                tracks_with_no_priorities.remove(track_id)

    queues.low.extend(tracks_with_no_priorities)

    return queues

