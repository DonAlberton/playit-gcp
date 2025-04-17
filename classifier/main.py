from fastapi import FastAPI
import requests
import json
from gcp import PubsubPublisherClient, PubsubSubscriberClient, FirestoreClient, TasksClient
from models import UsersByPriorities, Priorities
from requests.exceptions import HTTPError
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
async def start_classifier(input_playlist_id: str) -> None:
    users_priorities: UsersByPriorities = firestore_client.get_users_priorities(input_playlist_id)
    tracks: dict = fetch_tracks(input_playlist_id)
    classified: Priorities = classify_tracks(tracks, users_priorities)
    publisher.push_queues_messages(input_playlist_id, classified)
    # task_client.push_classifier_reprocessing(input_playlist_id)


@app.put("/priorities/{intput_playlist_id}")
def set_users_priorities(input_playlist_id: str, users_priorities: UsersByPriorities) -> None:
    
    if not firestore_client.does_playlist_exist(input_playlist_id):
        publisher.create_topics(input_playlist_id)
        subscriber: PubsubSubscriberClient = PubsubSubscriberClient()
        subscriber.create_subscriptions(input_playlist_id)

    firestore_client.update_users_priorities(input_playlist_id, users_priorities)


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

    users_dict = users_priorities.model_dump()

    for track in tracks:
        user_id = track["added_by_id"]
        track_id = track["track_id"]

        for priority, users_id in users_dict.items():
            if user_id in users_id:
                getattr(queues, priority).append(track_id)

    return queues

