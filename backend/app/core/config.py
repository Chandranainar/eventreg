from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./abn_registration.db"
    secret_key: str = "change-this-secret-key"
    access_token_expire_minutes: int = 60
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    cookie_secure: bool = False
    cookie_domain: str | None = None
    event_timezone: str = "Asia/Kolkata"
    public_event_id: str = "abn-2026"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = "Alpha Business Network"

    google_sheets_sync_enabled: bool = False
    google_sheet_id: str = ""
    google_service_account_file: str = ""

    rate_limit_registration: int = 10
    rate_limit_login: int = 8
    rate_limit_window_seconds: int = 60
    admin_cookie_name: str = "abn_admin_token"
    csrf_cookie_name: str = "abn_csrf_token"
    csrf_header_name: str = "X-CSRF-Token"
    max_upload_bytes: int = Field(default=2_000_000, ge=100_000)
    bootstrap_admin_name: str = ""
    bootstrap_admin_email: str = ""
    bootstrap_admin_password: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cookie_secure", "google_sheets_sync_enabled", mode="before")
    @classmethod
    def parse_bool(cls, value):
        if isinstance(value, str):
            return value.lower() in {"1", "true", "yes", "on"}
        return bool(value)

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


settings = Settings()
