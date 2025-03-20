# importerar.env filer, kan vara olika för olika klasser
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Two levels up from app/settings.py to reach the root where .env is located
env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    DB_URL: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_REGION: str
    S3_BUCKET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    MISTRAL_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8"
    )


settings = Settings()

DB_URL: str
