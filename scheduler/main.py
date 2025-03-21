from fastapi import FastAPI, Body
import uvicorn
from priorities import Priorities
import asyncio
import redis as redis
import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout
import json

import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI()

event = asyncio.Event()

PLAYIT_URL_BASE = os.getenv("PLAYIT_URL_BASE") # "http://127.0.0.1:8000"
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

rd = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

@app.post("/playlists")
def set_playlist(output_playlist: str = Body(...)):
    global output_playlist_id
    output_playlist_id = output_playlist

@app.post("/priorities")
async def add_priorities(priorities_dto: Priorities):
    # global priorities
    priorities.update(priorities_dto)

@app.get("/priorities")
async def get_priorities():
    return priorities

@app.post("/start")
async def start_scheduler():
    event.set()
    asyncio.create_task(pusher(event))

@app.post("/stop")
def stop_scheduler():
    event.clear()


output_playlist_id = "6EPla6iVCb3AlBizZaVyjt"

headers = { "Content-Type": "application/json" }

priorities = {
    "high": 3,
    "medium": 2,
    "low": 1
}

# TODO: Change sync redis to async
def pull_redis():
    with rd.pipeline() as pipe:
        for priority, value in priorities.items():
            # pipe.lrange(priority, 0, value-1)
            # pipe.ltrim(priority, value, -1)
            for _ in range(value):
                pipe.lpop(priority)

        output_playlist = pipe.execute()

    return [byte.decode('utf-8') for byte in output_playlist if byte]

# TODO: Change sync requests to async
def push_api(tracks_ids):
    if not tracks_ids:
        pass 

    try:
        response = requests.post(f"{PLAYIT_URL_BASE}/playlists/{output_playlist_id}/tracks", headers=headers, data=json.dumps(tracks_ids))        
        response.raise_for_status()
    
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status code: {response.status_code if response else 'No response'}")
    except ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

async def pusher(event):
    while event.is_set():
        values = pull_redis()
        push_api(values)
        # print("Pushed!")
        await asyncio.sleep(30)


async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=80)
    server = uvicorn.Server(config)

    await asyncio.create_task(server.serve())

if __name__ == "__main__":
    asyncio.run(main())