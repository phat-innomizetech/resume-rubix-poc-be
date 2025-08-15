from typing import Annotated, Any, Literal

from pydantic import (
    AnyUrl,
    BeforeValidator,
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Use top level .env file for settings
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    API_VERSION: str
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    API_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.API_CORS_ORIGINS]

    PROJECT_NAME: str
    LOGGING_CONFIG_FILE: str = "logging.ini"
    ENV_LOG_LEVEL: Literal["DEBUG", "INFO", "WARN", "ERROR"] = "DEBUG"
    HF_TOKEN: str
    GEMINI_API_KEY: str


settings = Settings()  # type: ignore
