from models.priorities import Priorities
from pydantic import BaseModel, Field


class PlaylistToPriorities(BaseModel):
    """
    Each playlist has 3 different priorities assigned, which stores 
    temporarily  
    """
    playlists: dict[str, Priorities] = Field(default_factory=dict)