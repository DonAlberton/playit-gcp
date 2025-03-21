from pydantic import BaseModel, Field

class Playlist(BaseModel):
    playlist_id: str
    name: str
    tracks: list = Field(default_factory=list, init=False)
