from pydantic import BaseModel
from typing import Optional


class StartSchedulerRequest(BaseModel):
    output_playlist_id: Optional[str] = None
    trigger_mode: str