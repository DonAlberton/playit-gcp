from pydantic import BaseModel, Field


class Priorities(BaseModel):
    low: list[str] = Field(default_factory=list)
    medium: list[str] = Field(default_factory=list)
    high: list[str] = Field(default_factory=list)