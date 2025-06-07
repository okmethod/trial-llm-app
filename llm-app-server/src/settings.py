import os
from functools import lru_cache

from pydantic_settings import BaseSettings

google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
default_region = os.getenv("DEFAULT_REGION")
llm_model = os.getenv("LLM_MODEL")
system_prompt = os.getenv("LLM_SYSTEM_PROMPT")


class Settings(BaseSettings):
    app_name: str = "Sample API"
    app_version: str = "0.1.0"

    allowed_origins: list[str] = []  # Set allowed origins as needed

    google_cloud_project: str | None = google_cloud_project
    default_region: str | None = default_region

    llm_model: str = llm_model or "gemini-1.5-flash"
    # APIキーは環境変数 GOOGLE_API_KEY で設定
    system_prompt: str = system_prompt or (
        "- あなたは親切で有能なAIアシスタントです。"
        "- ユーザーは日本人かつ日本語話者です。そのため、明確な指示がない限り、日本語で応答してください。"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
