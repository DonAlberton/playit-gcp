from pydantic import BaseModel

class UsersPriorities(BaseModel):
    low: list[str]
    medium: list[str]
    high: list[str]