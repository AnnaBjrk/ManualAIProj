from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# One level up from app/settings.py
env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    # Original fields
    DB_URL: str
    AWS_ACCESS_KEY: str
    AWS_SECRET_KEY: str
    AWS_REGION: str
    S3_BUCKET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    MISTRAL_API_KEY: str
    STORAGE_MODE: str
    LOCAL_UPLOAD_FOLDER: str

    # Additional fields from your .env file
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_HOST: str

    model_config = SettingsConfigDict(
        env_file=str(env_path),
        env_file_encoding="utf-8"
    )


settings = Settings()
