from pydantic import BaseModel
from typing import Optional

class SetUsersPrioritiesRequest(BaseModel):
    low: list[str]
    medium: list[str]
    high: list[str]


class SetQueuesWeightsRequest(BaseModel):
    low: int
    medium: int
    high: int


class StartClassifierRequest(BaseModel):
    trigger_mode: str


class StartSchedulerRequest(BaseModel):
    output_playlist_id: Optional[str] = None
    trigger_mode: str
