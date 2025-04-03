from abc import ABC, abstractmethod

class DatabaseRepository(ABC):
    
    @abstractmethod
    def playlist_exists(self, playlist_id: str) -> bool:
        pass

    @abstractmethod
    def save_playlist_id(self, playlist_id: str) -> None:
        pass

    @abstractmethod
    def save_user_id(self, playlist_id: str, user_id: str, username: str) -> None:
        pass

    @abstractmethod
    def get_users_ids(self, playlist_id: str) -> dict:
        pass

    @abstractmethod
    def delete_playlist_id(self, playlist_id: str) -> None:
        pass