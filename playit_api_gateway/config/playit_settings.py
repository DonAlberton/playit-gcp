from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(".") / ".env"
load_dotenv(dotenv_path=dotenv_path)

class PlayitSettings(BaseSettings):
    scheduler_url: str
    classifier_url: str
    playit_url: str
