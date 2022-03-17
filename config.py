import os

from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    api_key: str = os.getenv("API_KEY")
    base_api_url: AnyUrl = os.getenv("BASE_API_URL")
    redis_url: AnyUrl = os.getenv("REDIS_URL")

settings = Settings()
