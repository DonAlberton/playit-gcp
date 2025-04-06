from fastapi import FastAPI
import requests
import json
from gcp import PubsubPublisherClient, PubsubSubscriberClient, FirestoreClient
from models import UsersByPriorities, Priorities

PLAYIT_URL_BASE = "http://127.0.0.1:8000" # os.getenv("PLAYIT_URL_BASE")

publisher: PubsubPublisherClient = PubsubPublisherClient()
firestore_client: FirestoreClient = FirestoreClient()


app = FastAPI()

@app.post("/start/{input_playlist_id}")
async def start_classifier(input_playlist_id: str) -> None:
    users_priorities: UsersByPriorities = firestore_client.get_users_priorities(input_playlist_id)
    tracks: dict = fetch_tracks(input_playlist_id)
    classified: Priorities = classify_tracks(tracks, users_priorities)

    publisher.push_queues_messages(input_playlist_id, classified)


@app.put("/priorities")
def set_users_priorities(input_playlist_id: str, users_priorities: UsersByPriorities) -> None:
    
    if not firestore_client.does_playlist_exist(input_playlist_id):
        firestore_client.create_empty_document(input_playlist_id)
        publisher.create_topics(input_playlist_id)

        subscriber: PubsubSubscriberClient = PubsubSubscriberClient()
        subscriber.create_subscriptions(input_playlist_id)

    firestore_client.update_users_priorities(input_playlist_id, users_priorities)


def fetch_tracks(input_playlist_id: str) -> dict:
    response = requests.get(f"{PLAYIT_URL_BASE}/playlists/{input_playlist_id}/tracks")
    assert response.status_code == 200

    data = json.loads(response.content)

    tracks_ids = [track_data["track_id"] for track_data in data]

    headers = { "Content-Type": "application/json" }
    response = requests.delete(
        f"{PLAYIT_URL_BASE}/playlists/{input_playlist_id}/tracks",
        headers=headers, 
        data=json.dumps(tracks_ids)
    )
    assert response.status_code == 200

    return data


def classify_tracks(data: dict, users_priorities: UsersByPriorities) -> Priorities:
    queues = Priorities()

    users_dict = users_priorities.model_dump()

    for track in data:
        user_id = track["added_by_id"]
        track_id = track["track_id"]

        for priority, users_id in users_dict.items():
            if user_id in users_id:
                getattr(queues, priority).append(track_id)

    return queues

