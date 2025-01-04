import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from redis.asyncio import Redis, from_url

from tools_openverse.common.logger_ import setup_logger

logger = setup_logger("config")


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    DEBUG: bool = os.getenv("DEBUG")

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent

    # Database
    DATABASE_DRIVER: str = os.getenv("DATABASE_DRIVER")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT")
    REDIS_DB: Optional[int] = os.getenv("REDIS_DB")
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")

    # JWT Settings
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

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
        return f"{self.DATABASE_DRIVER}:///{self.BASE_DIR / self.DATABASE_NAME}"

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

    return await from_url(  # type: ignore
        settings_config.redis_url, decode_responses=True, encoding="utf-8"
    )


# Экспортируем settings для использования в других модулях
settings = get_settings()
