from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from redis.asyncio import Redis, from_url

from .logger_ import setup_logger

import os

logger = setup_logger("config")



class Settings(BaseSettings):
    PROJECT_NAME: str
    DEBUG: bool = False

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent

    # Database
    DATABASE_DRIVER: str = os.getenv("DATABASE_DRIVER")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")

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
        env_file=Path(__file__).parent.parent /  ".env", env_file_encoding="utf-8", case_sensitive=True
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


@lru_cache
def get_settings() -> Settings:

    settings = Settings()

    logger.info("Starting application with the following settings:")
    logger.info(f"PROJECT_NAME: {settings.PROJECT_NAME}")
    logger.info(f"DEBUG: {settings.DEBUG}")
    logger.info(f"DATABASE_URL: {settings.database_url}")
    logger.info(f"REDIS_URL: {settings.redis_url}")
    logger.info(f"ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
    logger.info(f"SESSION_TTL: {settings.SESSION_TTL}")

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

