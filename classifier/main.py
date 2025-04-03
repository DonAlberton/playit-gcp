from fastapi import FastAPI
import requests
import json
from users_priorities import UsersPriorities

from google.cloud import firestore, pubsub_v1
from google.api_core.exceptions import AlreadyExists
import redis



PLAYIT_URL_BASE = "http://127.0.0.1:8002" # os.getenv("PLAYIT_URL_BASE")

REDIS_HOST = "127.0.0.1" # os.getenv("REDIS_HOST")
REDIS_PORT = 6379 # os.getenv("REDIS_PORT")
rd = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)


project_id = "playground-454021"
publisher: pubsub_v1.PublisherClient = pubsub_v1.PublisherClient()

firestore_client: firestore.Client = firestore.Client()
document_name: str = "users_priorities"

"""
playlist_to_users_priorities: dict = {
    "input_playlist_id_1": {
        "low": ["user_id_1", "user_id_2"],
        "medium": ["user_id_3"],
        "high": ["user_id_4", "user_id_5"]
    },
    "input_playlist_id_2": ...
}
"""
playlist_to_users_priorities: dict = {}

def fetch_input_playlist(input_playlist_id: str) -> None:
    doc_ref = firestore_client.collection(document_name).document(input_playlist_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise ValueError(f"Playlist id {input_playlist_id} does not exist")
    
    playlist_to_users_priorities[input_playlist_id] = doc.to_dict()[input_playlist_id]

    if input_playlist_id not in input_playlists_to_priorities: 
        input_playlists_to_priorities[input_playlist_id] = UsersPriorities().model_dump()


"""
input_playlists_to_priorities = {
    "playlist_id_1": {
        "high": [],
        "medium": [],
        "low": []
    },
    "playlist_id_2": ...
}
"""
input_playlists_to_priorities: dict[str, dict] = {}


app = FastAPI()

@app.post("/start/{input_playlist_id}")
async def start_classifier(input_playlist_id: str) -> None:
    fetch_input_playlist(input_playlist_id)
    fetch_api(input_playlist_id)
    push_redis(input_playlist_id)


@app.put("/priorities")
def set_users_priorities(input_playlist_id: str, users_priorities: UsersPriorities) -> None:
    
    def create_pubsub_topics(input_playlist_id: str) -> None:
        priorities = {"low", "medium", "high"}
        topic_name_template = f"projects/{project_id}/topics"
        
        try:
            for priority in priorities:
                publisher.create_topic(name=f"{topic_name_template}/{priority}-{input_playlist_id}")
        except AlreadyExists as e:
            print(e)


    input_playlists_to_priorities[input_playlist_id] = users_priorities.model_dump()
    doc_ref = firestore_client.collection(document_name).document(input_playlist_id)

    doc = doc_ref.get()

    if not doc.exists:
        doc_ref.set({})
        create_pubsub_topics(input_playlist_id)

    doc_ref.update({input_playlist_id: users_priorities.model_dump()})


def fetch_api(input_playlist_id: str) -> None:
    queues = input_playlists_to_priorities[input_playlist_id]
    headers = { "Content-Type": "application/json" }

    response = requests.get(f"{PLAYIT_URL_BASE}/playlists/{input_playlist_id}/tracks")

    assert response.status_code == 200

    data = json.loads(response.content)

    tracks_ids = []
    priorities_assiged = playlist_to_users_priorities[input_playlist_id]

    for track in data:
        user_id = track["added_by_id"]

        for priority, users_id  in priorities_assiged.items():
            if user_id in users_id:
                queues[priority].append(track["track_id"])
                tracks_ids.append(track["track_id"])

    response = requests.delete(f"{PLAYIT_URL_BASE}/playlists/{input_playlist_id}/tracks", headers=headers, data=json.dumps(tracks_ids))
    
    assert response.status_code == 200


def push_redis(input_playlist_id: str) -> None:
    queues = input_playlists_to_priorities[input_playlist_id]

    with rd.pipeline() as pipe:
        for priority, queue in queues.items():
            if queue:
                pipe.rpush(f"{input_playlist_id}:{priority}", *queue)
                queue.clear()

        pipe.execute()

def push_pubsub_gcp(input_playlist_id: str) -> None:
    pass
