from fastapi import FastAPI, Body, HTTPException
import uvicorn
from authorization.token_refresh import token_refresh
from repositories.audio_streaming.base import TrackRepository, PlaylistRepository
from repositories.audio_streaming.spotify_playlist_repository import SpotifyPlaylistRepository
from repositories.audio_streaming.spotify_track_repository import SpotifyTrackRepository
from repositories.database.base import DatabaseRepository
from repositories.database.firestore_repository import FirestoreRepository
from models.playlist import Playlist


# Instead of saving the access token in .env, there is a new token created
# out of the refresh token (which is stored in the .env but does not change)
token = token_refresh()

playlist_repository: PlaylistRepository = SpotifyPlaylistRepository(token)
track_repository: TrackRepository = SpotifyTrackRepository(token)

# TODO: Complete repository "database_repository: DatabaseRepository = FirestoreRepository()"
database_repository: DatabaseRepository = FirestoreRepository()

app = FastAPI()

# Playlists ids with assigned users ids
# playlist_to_user_ids: dict = {
#     'playlist_id_1': {}, 
#     'playlist_id_2': {'user_id_1': 'username_1'}
# }


@app.post("/playlists")
def create_playlist(name: str = Body(...), is_public: bool = Body(True)):
    # TODO: Add is_public to App Gateway microservice
    playlist: Playlist = playlist_repository.create_playlist(name, is_public)

    database_repository.save_playlist_id(playlist.playlist_id)

    return playlist


@app.delete("/playlists/{playlist_id}")
def unfollow_playlist(playlist_id: str):
    # TODO: Delete firestore document with  when playlist is unfollowed
    playlist_repository.unfollow_playlist(playlist_id)
    database_repository.delete_playlist_id(playlist_id)


@app.post("/playlists/{playlist_id}/tracks/{track_id}")
def add_track(playlist_id: str, track_id: str):
    playlist_repository.add_track(playlist_id, track_id)


@app.get("/playlists/{playlist_id}/tracks")
def get_playlist_tracks(playlist_id: str):
    # TODO: Change with Depends
   
    if not database_repository.playlist_exists(playlist_id):
        raise HTTPException(status_code=404, detail=f"Playlist id {playlist_id} does not exist")
    
    users_ids = database_repository.get_users_ids(playlist_id)

    added_tracks = track_repository.get_added_tracks(playlist_id) 

    for track in added_tracks:
        if track.added_by_id not in users_ids:
            username = track_repository.get_user_name(track.added_by_id)
            database_repository.save_user_id(playlist_id, track.added_by_id, username)

    return added_tracks


@app.post("/playlists/{playlist_id}/tracks")
def add_tracks(playlist_id: str, tracks: list[str]):
    playlist_repository.add_tracks(playlist_id, tracks)


@app.delete("/playlists/{playlist_id}/tracks")
def delete_tracks(playlist_id: str, tracks_ids: list[str]):
    return track_repository.delete_tracks(playlist_id, tracks_ids)


@app.get("/playlists/{playlist_id}/users")
def get_playlists_users(playlist_id: str):

    if not database_repository.playlist_exists(playlist_id):
        raise HTTPException(status_code=404, detail=f"Playlist id {playlist_id} does not exist")
    
    added_tracks = track_repository.get_added_tracks(playlist_id) 

    users_ids = database_repository.get_users_ids(playlist_id)

    for track in added_tracks:
        if track.added_by_id not in users_ids:
            username = track_repository.get_user_name(track.added_by_id)
            database_repository.save_user_id(playlist_id, track.added_by_id, username)
            users_ids[track.added_by_id] = username

    return users_ids
