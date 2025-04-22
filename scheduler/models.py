from pydantic import BaseModel, Field
from typing import Optional, Literal

class QueueWeights(BaseModel):
    high: int = 3
    medium: int = 2
    low: int = 1


class QueuePriorities(BaseModel):
    high: list[str] = Field(default_factory=list)
    medium: list[str] = Field(default_factory=list)
    low: list[str] = Field(default_factory=list)


class StartSchedulerRequest(BaseModel):
    output_playlist_id: Optional[str] = None
    trigger_mode: str 


class StopSchedulerRequest(BaseModel):
    process_asset_flag: bool = False