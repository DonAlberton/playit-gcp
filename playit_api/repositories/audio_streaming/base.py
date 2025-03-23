from abc import ABC, abstractmethod
from models.track import Track
from models.playlist import Playlist

class PlaylistRepository(ABC):
    @abstractmethod
    def create_playlist(self, playlist_name: str, user_id: str, is_public: bool) -> Playlist:
        pass

    @abstractmethod
    def unfollow_playlist(self, playlist_id: str) -> None:
        pass

    @abstractmethod
    def add_track(self, playlist_id: str, track_id: str) -> None:
        pass
    
    @abstractmethod
    def add_tracks(self, playlist_id: str, tracks: list[str]) -> None:
        pass

class TrackRepository(ABC):
    @abstractmethod
    def get_user_name(self, user_id: str) -> str:
        pass

    @abstractmethod
    def get_added_tracks(self, playlist_id: str) -> list[Track]:
        pass

    @abstractmethod
    def delete_tracks(self, playlist_id: str, tracks_ids: list[str]) -> None:
        pass