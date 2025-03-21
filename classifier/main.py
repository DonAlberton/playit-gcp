from fastapi import FastAPI, Body
import uvicorn 

import redis
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout
import asyncio

import json

import os
from dotenv import load_dotenv
from pathlib import Path

from users_priorities import UsersPriorities

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

PLAYIT_URL_BASE = os.getenv("PLAYIT_URL_BASE")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

rd = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

app = FastAPI()

event = asyncio.Event()

# TODO: Change it so every user has a priority assigned (now the user is assigned to a priority)
priorities_assiged = {
    "low": {"11180277231"},
    "medium": {"31fg75dmlz25cosa7zgzw4gy6fr4", "pawełgolec"},
    "high": {"31qvemjqvhkkvdzfmkut24y4lsmy"}
}

input_playlist_id = "5w7pHgT0XZ4jU69Rq1wPPu" # "6EPla6iVCb3AlBizZaVyjt"

@app.post("/start")
async def start_classifier():
    event.set()
    asyncio.create_task(pull_push_loop(event))

@app.post("/stop")
async def stop_classifier():
    event.clear()

@app.post("/playlists")
def set_input_playlist(input_playlist: str = Body(...)):
    global input_playlist_id # Change not to use global variable (Depends on fast api feature instead)
    input_playlist_id = input_playlist

@app.get("/playlist")
def get_playlist():
    return input_playlist_id

@app.put("/priorities")
def set_users_priorities(users_priorities: UsersPriorities):
    global priorities_assiged # Change not to use global variable (Depends on fast api feature instead)
    priorities_assiged = users_priorities.model_dump()

@app.get("/priorities")
def get_users_priorities():
    return priorities_assiged

headers = { "Content-Type": "application/json" }

queues = {
    "high": [],
    "medium": [],
    "low": []
}

# TODO: Change sync requests to async
def fetch_api():
    try:
        response = requests.get(f"{PLAYIT_URL_BASE}/playlists/{input_playlist_id}/tracks")
        response.raise_for_status()

        data = json.loads(response.content)

        tracks_ids = []

        for track in data:
            user_id = track["added_by_id"]
            
            for priority, users_id  in priorities_assiged.items():
                if user_id in users_id:
                    queues[priority].append(track["track_id"])
                    tracks_ids.append(track["track_id"])

        response = requests.delete(f"{PLAYIT_URL_BASE}/playlists/{input_playlist_id}/tracks", headers=headers, data=json.dumps(tracks_ids))
        # response.raise_for_status()

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")
    except ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

# TODO: Change sync redis to async
def push_redis():
    with rd.pipeline() as pipe:
        for priority, queue in queues.items():
            if queue:
                pipe.rpush(priority, *queue)
                queue.clear()

        pipe.execute()

async def pull_push_loop(event):
    while event.is_set():
        fetch_api()
        # print("Fetched!")
        push_redis()
        # print("Pushed!")
        await asyncio.sleep(30)

async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=80)
    server = uvicorn.Server(config)

    await asyncio.create_task(server.serve())


# TODO: Change to main()
if __name__ == "__main__":
    asyncio.run(main())
