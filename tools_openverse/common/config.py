import logging
import os
from functools import cache
from pathlib import Path
from typing import Any, ClassVar, Optional

from dotenv import find_dotenv, load_dotenv
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from redis.asyncio import Redis, from_url  # pyright: ignore

from tools_openverse.common.logger_ import setup_logger

logger = setup_logger("config")


load_dotenv(find_dotenv(filename=".env", raise_error_if_not_found=True))


def get_env_value(key: str) -> Any:
    """Получаем значение переменной окружения"""

    result = os.getenv(key)
    if not result:
        return None
    return result


class Settings(BaseSettings):
    PROJECT_NAME: str = get_env_value("PROJECT_NAME")
    DEBUG: bool = get_env_value("DEBUG")

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent.parent.parent

    # Database
    ALLOWED_DATABASES: ClassVar[list[str]] = ["sqlite3", "postgresql"]

    # Database
    DATABASE_DB: str = get_env_value("DATABASE_NAME")
    DATABASE_DRIVER: str = get_env_value("DATABASE_DRIVER")
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_HOST: Optional[str] = get_env_value("DATABASE_HOST")
    DATABASE_PORT: Optional[str] = get_env_value("DATABASE_PORT")
    DATABASE_USER: Optional[str] = get_env_value("DATABASE_USER")
    DATABASE_PASSWORD: Optional[str] = get_env_value("DATABASE_PASSWORD")
    DATABASE_FILE_NAME: Optional[str] = get_env_value("DATABASE_FILE_NAME")
    DATABASE_NAME: Optional[str] = get_env_value("DATABASE_NAME")

    # Redis
    REDIS_HOST: str = get_env_value("REDIS_HOST")
    REDIS_PORT: int = get_env_value("REDIS_PORT")
    REDIS_DB: Optional[int] = get_env_value("REDIS_DB")
    REDIS_PASSWORD: Optional[str] = get_env_value("REDIS_PASSWORD")

    # JWT Settings
    JWT_ALGORITHM: str = get_env_value("JWT_ALGORITHM")
    JWT_SECRET_KEY: str = get_env_value("JWT_SECRET_KEY")

    ALL_SERVICES: ClassVar[list[str]] = ["USERS, AUTHETICATION, TEST"]
    OTHER_SERVICES: str = get_env_value("OTHER_SERVICES")
    BASE_URL: str = get_env_value("BASE_URL")
    PORT_SERVICE: str | int | None = Field(default=None)

    PORT_SERVICE_AUTH: str | int | None = get_env_value("PORT_SERVICE_AUTH")
    PORT_SERVICE_USERS: str | int | None = get_env_value("PORT_SERVICE_TEST")

    # Session
    SESSION_TTL: int = 3600

    @property
    def database_url(self) -> Optional[str]:
        """Формируем URL для подключения к базе данных"""
        if self.DATABASE_DB == "sqlite3":
            return (
                f"{self.DATABASE_DRIVER}:///{self.BASE_DIR / self.DATABASE_FILE_NAME}"
                if self.DATABASE_FILE_NAME
                else None
            )
        if self.DATABASE_DB == "postgresql":
            url = (
                f"{self.DATABASE_DRIVER}://"
                f"{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}"
                f"/{self.DATABASE_NAME}"
            )

            logger.debug(f"Formed url {url}")
            return url
        raise ValueError(f"Unsupported database: {self.DATABASE_DB}")

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
        other_services = os.getenv("OTHER_SERVICES", "").split(", ")

        if not other_services:
            raise ValueError("OTHER_SERVICES environment variable is empty or not set")

        if value in other_services:
            raise ValueError(f"PROJECT_NAME '{value}' must be one of: {', '.join(other_services)}")

        return value

    @field_validator("DATABASE_DB")
    @classmethod
    def validate_database_name(cls, value: str) -> str:
        value = value.lower()
        if value not in Settings.ALLOWED_DATABASES:
            raise ValueError(f"Database {value}must be one of {Settings.ALLOWED_DATABASES}")

        if value == "postgresql":
            required_vars = [
                "DATABASE_HOST",
                "DATABASE_PORT",
                "DATABASE_USER",
                "DATABASE_PASSWORD",
            ]
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                raise ValueError(
                    f"Missing required environment variables for PostgreSQL: {
                        ', '.join(missing_vars)}"
                )
        elif value == "sqlite3":
            if not os.getenv("DATABASE_FILE_NAME"):
                raise ValueError("Missing DATABASE_FILE_NAME for SQLite")

        return value

    @model_validator(mode="before")
    @classmethod
    def validate_port_services(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Валидация портов для сервисов"""
        if values.get("PROJECT_NAME") == "USERS":
            if not values.get("PORT_SERVICE_USERS"):
                raise ValueError("PORT_SERVICE_USERS is required for USERS service")
            values["PORT_SERVICE"] = values["PORT_SERVICE_USERS"]

        elif values.get("PROJECT_NAME") == "AUTHETICATION":
            if not values.get("PORT_SERVICE_AUTH"):
                raise ValueError("PORT_SERVICE_AUTH is required for AUTHETICATION service")
            values["PORT_SERVICE"] = values["PORT_SERVICE_AUTH"]

        else:
            if not values.get("PORT_SERVICE_AUTH") and not values.get("PORT_SERVICE_USERS"):
                raise ValueError(
                    "PORT_SERVICE_AUTH or PORT_SERVICE_USERS is required for TEST service"
                )

        return values


@cache
def get_settings() -> Settings:

    settings_ = Settings()
    settings_.log_settings(logger)
    return settings_


# Экспортируем settings для использования в других модулях
settings = get_settings()


# Создаем асинхронное подключение к Redis
async def get_redis() -> Redis:
    """
    Создаем подключение к Redis с настройками из конфигурации
    """

    return await from_url(  # type: ignore
        settings.redis_url, decode_responses=True, encoding="utf-8"
    )
