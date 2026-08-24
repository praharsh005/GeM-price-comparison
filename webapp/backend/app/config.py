from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "GeM Price Intelligence"
    database_url: str = "postgresql+psycopg2://gem:gem@localhost:5432/gem_unified"
    redis_url: str = "redis://localhost:6379/0"

    scraper_rate_limit: float = 2.0
    scraper_max_pages: int = 15


settings = Settings()
