from fastapi import FastAPI, Body
import uvicorn
import os
from dotenv import load_dotenv
from authorization.token_refresh import token_refresh
from repositories.playlist_repository import PlaylistRepository
from repositories.track_repository import TrackRepository
from models.playlist import Playlist
import asyncio
from pathlib import Path

env_path = Path(".") / ".env"

load_dotenv(dotenv_path=env_path)

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

# Instead of saving the access token in .env, there is a new token created
# out of the refresh token (which is stored in the .env but does not change)
token = token_refresh()

playlist_repository = PlaylistRepository(token)
track_repository = TrackRepository(token)

app = FastAPI()

# TODO: Change to Redis to store the users corresponding to the playlist  
# to separate the responsibility of the REST API (longer network calls).

# Playlists ids with assigned users ids
playlist_to_user_ids = {"0eMFYVCMIOuz57wD08kBOm": {}}

async def update_token():
    while True:
        await asyncio.sleep(3595)
        new_token = token_refresh()
        playlist_repository.update_token(new_token)
        track_repository.update_token(new_token)


@app.on_event("startup")
async def start_background_task():
    asyncio.create_task(update_token())


@app.post("/playlists")
def create_playlist(name: str = Body(...), user_id: str = Body(...)):
    playlist: Playlist = playlist_repository.create_playlist(name, user_id)

    playlist_to_user_ids[playlist.playlist_id] = {}

    return playlist

@app.delete("/playlists/{playlist_id}")
def unfollow_playlist(playlist_id: str):
    playlist_repository.unfollow_playlist(playlist_id)


@app.post("/playlists/{playlist_id}/tracks/{track_id}")
def add_track(playlist_id: str, track_id: str):
    playlist_repository.add_track(playlist_id, track_id)

@app.get("/playlists/{playlist_id}/tracks")
def get_playlist_tracks(playlist_id: str):
    # TODO: Change with Depends
    global playlist_to_user_ids

    # Updates the dictionary of users that put tracks in the playlist
    # when this method is triggered

    

    for track in track_repository.get_added_tracks(playlist_id):
        if track.added_by_id not in playlist_to_user_ids[playlist_id]:
            playlist_to_user_ids[playlist_id][track.added_by_id] = track_repository.get_user_name(track.added_by_id)
            
    return track_repository.get_added_tracks(playlist_id)

@app.post("/playlists/{playlist_id}/tracks")
def add_tracks(playlist_id: str, tracks: list[str]):
    playlist_repository.add_tracks(playlist_id, tracks)

@app.delete("/playlists/{playlist_id}/tracks")
def delete_tracks(playlist_id: str, tracks_ids: list[str]):
    return track_repository.delete_tracks(playlist_id, tracks_ids)

@app.get("/playlists/{playlist_id}/users")
def get_playlists_users(playlist_id: str):
    for track in track_repository.get_added_tracks(playlist_id):
        if track.added_by_id not in playlist_to_user_ids[playlist_id]:
            playlist_to_user_ids[playlist_id][track.added_by_id] = track_repository.get_user_name(track.added_by_id)

    if playlist_id in playlist_to_user_ids:
        return playlist_to_user_ids[playlist_id]

async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=80)
    server = uvicorn.Server(config)

    await asyncio.create_task(server.serve())


if __name__ == "__main__":
    asyncio.run(main())