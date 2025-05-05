from pydantic import BaseModel


class StartClassifierRequest(BaseModel):
    trigger_mode: str