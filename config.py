from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "O Destaque API"
    environment: str = "development"
    # Definida no .env em produção; este valor serve apenas de exemplo local.
    database_url: str = "postgresql+psycopg://odestaque:change-me@127.0.0.1:5432/odestaque"
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = Field(default=30, ge=5, le=1440)
    refresh_token_days: int = Field(default=14, ge=1, le=90)
    cors_origins: str = "http://localhost:3000"
    upload_dir: Path = Path("uploads")
    max_upload_bytes: int = Field(default=5_000_000, ge=1)
    image_webp_quality: int = Field(default=82, ge=1, le=100)
    wordpress_api_url: str = "https://odestaque.co.mz/wp-json/wp/v2"
    skywallet_base_url: str = "https://skywallet-api.bluesparkmz.com"
    skywallet_sk_id: str | None = None
    skywallet_api_key: str | None = None
    admin_email: str | None = None
    admin_password: str | None = None
    admin_username: str = "admin"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def cors_origin_list(self) -> list[str]: return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
@lru_cache
def settings() -> Settings: return Settings()
