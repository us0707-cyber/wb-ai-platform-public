from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "WB AI Platform"
    app_env: str = "development"
    app_version: str = "3.0.0-alpha.6"
    secret_key: str = "change-this-secret-key"
    access_token_expire_minutes: int = 1440
    database_url: str = "sqlite:///./wb_ai.db"
    redis_url: str = "redis://redis:6379/0"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    ai_provider: str = "local"
    ai_request_timeout_seconds: int = 60
    job_worker_enabled: bool = True
    job_worker_poll_seconds: float = 1.0
    scheduler_enabled: bool = True
    scheduler_poll_seconds: float = 5.0
    wb_content_api_base: str = "https://content-api.wildberries.ru"
    wb_statistics_api_base: str = "https://statistics-api.wildberries.ru"
    wb_advert_api_base: str = "https://advert-api.wildberries.ru"
    wb_feedbacks_api_base: str = "https://feedbacks-api.wildberries.ru"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
