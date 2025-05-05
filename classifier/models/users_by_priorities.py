from pydantic import BaseModel, Field


class UsersByPriorities(BaseModel):
    low: set[str] = Field(default_factory=set)
    medium: set[str] = Field(default_factory=set)
    high: set[str] = Field(default_factory=set)