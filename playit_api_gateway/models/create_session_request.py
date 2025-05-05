from pydantic import BaseModel


class CreateSessionRequest(BaseModel):
    input_playlist_name: str