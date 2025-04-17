from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path(".") / ".env"
load_dotenv(dotenv_path=dotenv_path)

class GcpSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GCP_")

    project_id: str
    queue_id: str
    cloudtask_location: str
    classifier_retry_url: str
    queue_id: str

