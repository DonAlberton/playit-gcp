from models.users_by_priorities import UsersByPriorities
from pydantic import BaseModel, Field


class PlaylistToUsersPriorities(BaseModel):
    """
    Each user in the playlist is assigned to a specific priority 
    """
    playlists: dict[str, UsersByPriorities] = Field(default_factory=dict)