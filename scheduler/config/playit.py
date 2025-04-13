from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(".") / ".env"
load_dotenv(dotenv_path=dotenv_path)


class PlayitSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PLAYIT_")
    url: str