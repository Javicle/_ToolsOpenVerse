import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from dotenv import find_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from redis.asyncio import Redis  # type: ignore[PylancereportUnknownVariableType]
from redis.asyncio import from_url  # type: ignore[PylancereportUnknownVariableType]

from tools_openverse.common.logger_ import setup_logger

logger = setup_logger("config")


def get_env_value(key: str) -> Any:
    """Получаем значение переменной окружения"""
    result = os.getenv(key)
    if not result:
        raise ValueError(f"Environment variable '{key}' not found")
    return result


class Settings(BaseSettings):
    PROJECT_NAME: str = get_env_value("PROJECT_NAME")
    DEBUG: bool = get_env_value("DEBUG")

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent

    # Database
    ALLOWED_DATABASES: list[str] = ["sqlite3", "postgresql"]

    # Database
    DATABASE_NAME: str = get_env_value("DATABASE_NAME")
    DATABASE_DRIVER: str = get_env_value("DATABASE_DRIVER")
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_HOST: Optional[str] = get_env_value("DATABASE_HOST")
    DATABASE_PORT: Optional[str] = get_env_value("DATABASE_PORT")
    DATABASE_USER: Optional[str] = get_env_value("DATABASE_USER")
    DATABASE_PASSWORD: Optional[str] = get_env_value("DATABASE_PASSWORD")
    DATABASE_FILE_NAME: str = get_env_value("DATABASE_FILE_NAME")

    # Redis
    REDIS_HOST: str = get_env_value("REDIS_HOST")
    REDIS_PORT: int = get_env_value("REDIS_PORT")
    REDIS_DB: Optional[int] = get_env_value("REDIS_DB")
    REDIS_PASSWORD: Optional[str] = get_env_value("REDIS_PASSWORD")

    # JWT Settings
    JWT_ALGORITHM: str = get_env_value("JWT_ALGORITHM")
    JWT_SECRET_KEY: str = get_env_value("JWT_SECRET_KEY")

    ALL_SERVICES: list[str] = ["USERS, AUTHETICATION, TEST"]
    OTHER_SERVICES: str = get_env_value("OTHER_SERVICES")
    BASE_URL: str = get_env_value("BASE_URL")
    PORT_SERVICE: str | int = get_env_value("PORT_SERVICE")

    # Session
    SESSION_TTL: int = 3600

    model_config = SettingsConfigDict(
        env_file=find_dotenv(filename=".env", raise_error_if_not_found=True),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @property
    def database_url(self) -> str:
        """Формируем URL для подключения к базе данных"""
        if self.DATABASE_NAME == "sqlite3":
            return f"{self.DATABASE_DRIVER}:///{self.BASE_DIR / self.DATABASE_FILE_NAME}"
        elif self.DATABASE_NAME == "postgresql":
            return (
                f"{self.DATABASE_DRIVER}://"
                f"{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}"
                f"/{self.DATABASE_NAME}"
            )
        raise ValueError(f"Unsupported database: {self.DATABASE_NAME}")

    @property
    def redis_url(self) -> str:
        """Формируем URL для подключения к Redis"""
        auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}"

    def log_settings(self, logger_: logging.Logger) -> None:
        settings_dict = self.model_dump(exclude={"JWT_SECRET_KEY", "REDIS_PASSWORD"})
        logger_.info(f"Settings: {settings_dict}")
        for key, value in settings_dict.items():
            logger_.info(f"{key}: {value}")

    @field_validator("PROJECT_NAME")
    @classmethod
    def validate_project_name(cls, value: str) -> str:
        other_services = os.getenv("OTHER_SERVICES", "").split()

        if not other_services:
            raise ValueError("OTHER_SERVICES environment variable is empty or not set")

        if value in other_services:
            raise ValueError(f"PROJECT_NAME '{value}' must be one of: {', '.join(other_services)}")

        return value

    @field_validator("DATABASE_NAME")
    @classmethod
    def validate_database_name(cls, value: str) -> str:
        value = value.lower()
        if value not in cls.ALLOWED_DATABASES:
            raise ValueError(f"Database {value}must be one of {cls.ALLOWED_DATABASES}")

        if value == "postgresql":
            required_vars = ["DATABASE_HOST", "DATABASE_PORT", "DATABASE_USER", "DATABASE_PASSWORD"]
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                raise ValueError(
                    f"Missing required environment variables for PostgreSQL: {', '.join(missing_vars)}"
                )
        elif value == "sqlite3":
            if not os.getenv("DATABASE_FILE_NAME"):
                raise ValueError("Missing DATABASE_FILE_NAME for SQLite")

        return value


@lru_cache
def get_settings() -> Settings:

    settings = Settings()
    settings.log_settings(logger)
    return settings


# Создаем асинхронное подключение к Redis
async def get_redis() -> Redis:
    """
    Создаем подключение к Redis с настройками из конфигурации
    """
    settings_config = get_settings()

    return await from_url(settings_config.redis_url, decode_responses=True, encoding="utf-8")


# Экспортируем settings для использования в других модулях
settings = get_settings()
