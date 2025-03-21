from pydantic import BaseModel

class Priorities(BaseModel):
    low: int
    medium: int
    high: int