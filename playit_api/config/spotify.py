from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(".") / ".env"
load_dotenv(dotenv_path=dotenv_path)

class SpotifyConfig(BaseSettings):
    client_id: str
    client_secret: str
    redirect_url: str
    authentication_url: str = Field(alias="SPOTIFY_AUTHENTICATION_URL")
    access_token: str = Field(alias="SPOTIFY_ACCESS_TOKEN")
    refresh_token: str = Field(alias="SPOTIFY_REFRESH_TOKEN")
    api_url: str = Field(alias="SPOTIFY_API_URL")
