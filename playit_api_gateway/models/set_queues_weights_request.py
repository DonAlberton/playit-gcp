from pydantic import BaseModel


class SetQueuesWeightsRequest(BaseModel):
    low: int
    medium: int
    high: int