from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_PREFIX: str = "/api"

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""

    DATABASE_URL: str = ""

    ALLOWED_ORIGINS: str = ""

    DEBUG: bool = True

    @model_validator(mode="after")
    def build_database_url(self) -> Settings:
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return self

    CLA_HOST: str = ""
    CLA_IDENTIFIER: str = ""
    CLA_CALLBACK_URL: str = "http://localhost:5173/api/auth/cla/callback"

    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_COOKIE_SECURE: bool = False
    SESSION_TTL_DAYS: int = 30

    # Email settings
    EMAIL_ENABLED: bool = False
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@matos-clap.local"
    SMTP_FROM_NAME: str = "Matos CLAP"
    SMTP_USE_TLS: bool = True

    # Loan notification settings
    LOAN_REMINDER_DAYS_BEFORE: int = 2
    LOAN_NOTIFICATIONS_INTERVAL_HOURS: int = 24

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> list[str]:
        return v.split(",") if v else []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
