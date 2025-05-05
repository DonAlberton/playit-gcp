from pydantic import BaseModel


class QueueWeights(BaseModel):
    high: int = 3
    medium: int = 2
    low: int = 1