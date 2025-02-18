#importerar.env filer, kan vara olika för olika klasser
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent.parent / ".env"



class Settings(BaseSettings):
    DB_URL: str

    model_config = SettingsConfigDict(env_file=str(env_path))
    

settings = Settings()
