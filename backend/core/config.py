from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""

    DATABASE_URL: str = ""

    ALLOWED_ORIGINS: str = ""

    ENV: str = "production"
    ENABLE_DEV_LOGIN: bool = False
    LOG_LEVEL: str = "INFO"

    MEDIA_DIR: str = "data/media"

    @model_validator(mode="after")
    def build_database_url(self) -> Settings:
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return self

    CLA_ISSUER: str = ""
    CLA_CLIENT_ID: str = "matos-clap"
    CLA_CLIENT_SECRET: str = ""
    CLA_REDIRECT_URI: str = ""
    SECRET_KEY: str = ""

    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_TTL_DAYS: int = 30

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> list[str]:
        return v.split(",") if v else []

    @model_validator(mode="after")
    def require_oidc_settings(self) -> Settings:
        if self.ENV != "production" or self.ENABLE_DEV_LOGIN:
            return self
        required = ("CLA_ISSUER", "CLA_CLIENT_SECRET", "CLA_REDIRECT_URI", "SECRET_KEY")
        if missing := [name for name in required if not getattr(self, name)]:
            raise ValueError(f"Missing required settings: {', '.join(missing)}")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
