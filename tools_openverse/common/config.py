"""
Configuration module for the application.

This module provides settings management using Pydantic for validation
and environment variable loading. It supports multiple databases
(SQLite, PostgreSQL) and Redis configuration.
"""

import logging
import os
from pathlib import Path
from typing import Any, ClassVar, Optional

from dotenv import find_dotenv, load_dotenv
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from redis.asyncio import Redis, from_url  # pyright: ignore

from tools_openverse.common.logger_ import setup_logger

logger = setup_logger("config")

# Load environment variables from .env file
load_dotenv(find_dotenv(filename=".env", raise_error_if_not_found=True))


def get_env_value(key: str) -> Any:
    """
    Get environment variable value.

    Args:
        key (str): Environment variable name

    Returns:
        Any: Environment variable value or None if not found
    """
    result = os.getenv(key)
    if not result:
        return None
    return result


class Settings(BaseSettings):
    """
    Application settings class with validation.

    This class manages all application configuration using Pydantic
    for validation and type safety. Settings are loaded from environment
    variables with proper validation for required fields.

    Attributes:
        PROJECT_NAME (str): Name of the current project/service
        DEBUG (bool): Debug mode flag
        BASE_DIR (Path): Base directory path for the project
        DATABASE_* (str): Database connection parameters
        REDIS_* (str/int): Redis connection parameters
        JWT_* (str): JWT authentication settings
        SESSION_TTL (int): Session time-to-live in seconds
    """

    # Basic application settings
    PROJECT_NAME: str = get_env_value("PROJECT_NAME")
    DEBUG: bool = get_env_value("DEBUG")

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent.parent.parent

    # Database configuration
    ALLOWED_DATABASES: ClassVar[list[str]] = ["sqlite3", "postgresql"]

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

    # Redis configuration
    REDIS_HOST: str = get_env_value("REDIS_HOST")
    REDIS_PORT: int = get_env_value("REDIS_PORT")
    REDIS_DB: Optional[int] = get_env_value("REDIS_DB")
    REDIS_PASSWORD: Optional[str] = get_env_value("REDIS_PASSWORD")

    # JWT Settings
    JWT_ALGORITHM: str = get_env_value("JWT_ALGORITHM")
    JWT_SECRET_KEY: str = get_env_value("JWT_SECRET_KEY")

    # Service configuration
    ALL_SERVICES: ClassVar[list[str]] = ["USERS, AUTHETICATION, TEST"]
    OTHER_SERVICES: str = get_env_value("OTHER_SERVICES")
    BASE_URL: str = get_env_value("BASE_URL")
    PORT_SERVICE: str | int | None = Field(default=None)

    PORT_SERVICE_AUTH: str | int | None = get_env_value("PORT_SERVICE_AUTH")
    PORT_SERVICE_USERS: str | int | None = get_env_value("PORT_SERVICE_TEST")

    # Session configuration
    SESSION_TTL: int = 3600  # Session time-to-live in seconds (1 hour)

    @property
    def database_url(self) -> Optional[str]:
        """
        Generate database connection URL based on database type.

        Supports both SQLite and PostgreSQL databases. For SQLite,
        creates a file-based URL. For PostgreSQL, creates a network URL
        with authentication credentials.

        Returns:
            Optional[str]: Database connection URL or None if invalid config

        Raises:
            ValueError: If unsupported database type is specified
        """
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

            logger.debug(f"Formed database URL: {url}")
            return url
        raise ValueError(f"Unsupported database: {self.DATABASE_DB}")

    @property
    def redis_url(self) -> str:
        """
        Generate Redis connection URL.

        Creates a Redis URL with optional password authentication.

        Returns:
            str: Redis connection URL in format redis://[password@]host:port
        """
        auth_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}"

    def log_settings(self, logger_: logging.Logger) -> None:
        """
        Log all settings values (excluding sensitive data).

        Args:
            logger_ (logging.Logger): Logger instance to use for output
        """
        settings_dict = self.to_dict()
        for key, value in settings_dict.items():
            logger_.info(f"{key}: {value}")

    def to_dict(self) -> dict[str, Any]:
        """
        Convert settings to dictionary, excluding sensitive fields.

        Returns:
            dict[str, Any]: Settings dictionary without sensitive data
        """
        return self.model_dump(exclude={"JWT_SECRET_KEY", "REDIS_PASSWORD"})

    @field_validator("PROJECT_NAME")
    @classmethod
    def validate_project_name(cls, value: str) -> str:
        """
        Validate that PROJECT_NAME is one of allowed services.

        Args:
            value (str): Project name to validate

        Returns:
            str: Validated project name

        Raises:
            ValueError: If project name is not in allowed services list
        """
        other_services = os.getenv("OTHER_SERVICES", "").split(", ")

        if not other_services:
            raise ValueError("OTHER_SERVICES environment variable is empty or not set")

        if value in other_services:
            raise ValueError(
                f"PROJECT_NAME '{value}' must be one of: {', '.join(other_services)}"
            )

        return value

    @field_validator("DATABASE_DB")
    @classmethod
    def validate_database_name(cls, value: str) -> str:
        """
        Validate database type and required environment variables.

        Ensures that the specified database type is supported and all
        required environment variables are set for the chosen database.

        Args:
            value (str): Database type to validate

        Returns:
            str: Validated database type in lowercase

        Raises:
            ValueError: If database type is unsupported or required vars are missing
        """
        value = value.lower()
        if value not in Settings.ALLOWED_DATABASES:
            raise ValueError(
                f"Database {value} must be one of {Settings.ALLOWED_DATABASES}"
            )

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
        """
        Validate and set service ports based on project type.

        Each service type requires specific port configuration. This validator
        ensures the correct port is set based on the PROJECT_NAME.

        Args:
            values (dict[str, Any]): Dictionary of field values

        Returns:
            dict[str, Any]: Updated values with PORT_SERVICE set

        Raises:
            ValueError: If required port is not configured for the service type
        """
        if values.get("PROJECT_NAME") == "USERS":
            if not values.get("PORT_SERVICE_USERS"):
                raise ValueError("PORT_SERVICE_USERS is required for USERS service")
            values["PORT_SERVICE"] = values["PORT_SERVICE_USERS"]

        elif values.get("PROJECT_NAME") == "AUTHETICATION":
            if not values.get("PORT_SERVICE_AUTH"):
                raise ValueError(
                    "PORT_SERVICE_AUTH is required for AUTHETICATION service"
                )
            values["PORT_SERVICE"] = values["PORT_SERVICE_AUTH"]

        else:
            if not values.get("PORT_SERVICE_AUTH") and not values.get(
                "PORT_SERVICE_USERS"
            ):
                raise ValueError(
                    "PORT_SERVICE_AUTH or PORT_SERVICE_USERS"
                    "is required for TEST service"
                )

        return values


def get_settings() -> Settings:
    """
    Create and return application settings instance.

    This function creates a Settings instance, logs all configuration
    values, and returns the configured settings object.

    Returns:
        Settings: Configured and validated settings instance
    """
    settings_ = Settings()
    settings_.log_settings(logger)
    return settings_


# Export settings instance for use in other modules
settings = get_settings()


def get_redis() -> Redis:
    """
    Create and return Redis connection.

    Creates an asynchronous Redis connection using the configuration
    settings. The connection is configured with UTF-8 encoding and
    response decoding enabled.

    Returns:
        Redis: Configured async Redis connection instance

    Example:
        >>> redis_client = await get_redis()
        >>> await redis_client.set("key", "value")
        >>> value = await redis_client.get("key")
    """
    return from_url(  # type: ignore
        settings.redis_url, decode_responses=True, encoding="utf-8"
    )
