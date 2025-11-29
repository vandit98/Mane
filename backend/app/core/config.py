from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/trayashop"
    gemini_api_key: str = ""
    embedding_model: str = "models/embedding-001"
    chat_model: str = "models/gemini-2.0-flash"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
