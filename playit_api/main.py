from fastapi import FastAPI, Body
import uvicorn
from authorization.token_refresh import token_refresh
from repositories.audio_streaming.spotify_playlist_repository import SpotifyPlaylistRepository
from repositories.audio_streaming.spotify_track_repository import SpotifyTrackRepository
from models.playlist import Playlist
import asyncio

# Instead of saving the access token in .env, there is a new token created
# out of the refresh token (which is stored in the .env but does not change)
token = token_refresh()

playlist_repository = SpotifyPlaylistRepository(token)
track_repository = SpotifyTrackRepository(token)

app = FastAPI()

# TODO: Change to Firestore to store the users corresponding to the playlist  
# to separate the responsibility of the REST API (longer network calls).

# Playlists ids with assigned users ids
playlist_to_user_ids = {"0eMFYVCMIOuz57wD08kBOm": {}}


@app.post("/playlists")
def create_playlist(name: str = Body(...), user_id: str = Body(...), is_public: bool = Body(True)):
    # TODO: Add is_public to App Gateway microservice
    playlist: Playlist = playlist_repository.create_playlist(name, user_id, is_public)

    playlist_to_user_ids[playlist.playlist_id] = {}

    return playlist


@app.delete("/playlists/{playlist_id}")
def unfollow_playlist(playlist_id: str):
    # TODO: Delete firestore document with  when playlist is unfollowed
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
   
    # FIXME: When restarting the app, the system has no persistance to 
    # store playlist_to_user_ids dictionary

    # TODO: Store playlist_to_user_ids data in Firestore and fetch
    # every time the microservice is restarts

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

    # FIXME: When restarting the app, the system has no persistance to 
    # store playlist_to_user_ids dictionary

    # TODO: Store playlist_to_user_ids data in Firestore and fetch
    # every time the microservice is restarts
    for track in track_repository.get_added_tracks(playlist_id):
        if track.added_by_id not in playlist_to_user_ids[playlist_id]:
            playlist_to_user_ids[playlist_id][track.added_by_id] = track_repository.get_user_name(track.added_by_id)

    if playlist_id in playlist_to_user_ids:
        return playlist_to_user_ids[playlist_id]
