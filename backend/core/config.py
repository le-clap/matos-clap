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

    DEBUG: bool = False

    @model_validator(mode="after")
    def build_database_url(self) -> Settings:
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return self

    CLA_HOST: str = "https://centralelilleassos.fr"
    CLA_IDENTIFIER: str = "matos-clap"

    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_COOKIE_SECURE: bool = False
    SESSION_TTL_DAYS: int = 30

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> list[str]:
        return v.split(",") if v else []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
