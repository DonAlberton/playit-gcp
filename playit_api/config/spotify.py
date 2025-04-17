from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(".") / ".env"
load_dotenv(dotenv_path=dotenv_path)

class SpotifyConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='SPOTIFY_')

    client_id: str 
    user_id: str
    client_secret: str
    redirect_url: str
    authentication_url: str
    access_token: str
    refresh_token: str
    api_url: str
