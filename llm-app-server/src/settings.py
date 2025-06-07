import os
from functools import lru_cache

from pydantic_settings import BaseSettings

google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
default_region = os.getenv("DEFAULT_REGION")


class Settings(BaseSettings):
    app_name: str = "Sample API"
    app_version: str = "0.1.0"

    allowed_origins: list[str] = []  # Set allowed origins as needed

    google_cloud_project: str | None = google_cloud_project
    default_region: str | None = default_region

    llm_model: str = "gemini-2.0-flash"
    # APIキーは環境変数 GOOGLE_API_KEY で設定


@lru_cache
def get_settings() -> Settings:
    return Settings()
