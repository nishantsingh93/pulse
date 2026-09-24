from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://pulse:pulse@localhost:5432/pulse"
    cors_origins: str = "http://localhost:3000"
    oidc_issuer: str = ""
    oidc_audience: str = ""
    oidc_jwks_url: str = ""
    dev_token: str = ""
    x_bearer_token: str = ""
    youtube_api_key: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_user_agent: str = "PulsePOC/0.1"
    x_estimated_cost_cents: int = 0
    youtube_estimated_cost_cents: int = 0
    reddit_estimated_cost_cents: int = 0


@lru_cache
def settings() -> Settings:
    return Settings()
