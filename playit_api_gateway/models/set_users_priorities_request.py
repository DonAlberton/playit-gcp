from pydantic import BaseModel


class SetUsersPrioritiesRequest(BaseModel):
    low: list[str]
    medium: list[str]
    high: list[str]