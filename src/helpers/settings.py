"""
Application configuration settings loaded from environment variables.

This module provides a Settings class that loads configuration from:
1. .env file
2. Environment variables
3. Default values
"""

import sys
from typing import List, Literal
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings configuration.

    Uses Pydantic for validation and type conversion.
    Environment variables take precedence over .env file values.
    """

    # Application Configuration
    app_name: str = Field(..., env="APP_NAME", description="Name of the application")
    app_env: Literal["development", "production", "staging"] = Field("development", env="APP_ENV")
    app_secret: str = Field(..., env="APP_SECRET", description="Secret key for the application")
    app_debug: bool = Field(False, env="APP_DEBUG")

    # Database Configuration
    db_host: str = Field("localhost", env="DB_HOST")
    db_port: int = Field(5432, env="DB_PORT")
    db_name: str = Field(..., env="DB_NAME")
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")

    # API Configuration
    api_key: str = Field(..., env="API_KEY")
    api_timeout: int = Field(30, env="API_TIMEOUT")

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        "INFO", env="LOG_LEVEL")
    log_file: str = Field("app.log", env="LOG_FILE")

    FILE_TYPES: List[str] = Field(..., env="FILE_TYPES")
    DOC_LOCATION_SAVE: str = Field(..., env="DOC_LOCATION_SAVE")
    SPLLITER: str = Field(..., env="SPLLITER")
    CHUNKS_SIZE: int = Field(..., env="CHUNKS_SIZE")
    CHUNKS_OVERLAB: int = Field(..., env="CHUNKS_OVERLAB")
    # pylint: disable=too-few-public-methods
    class Config:
        """
        Pydantic configuration for environment file loading.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    """
    Get application settings with singleton pattern.

    Returns:
        Settings: Configured settings instance.
    """
    try:
        return Settings()
    except ValidationError as e:
        print("Error loading application settings:", file=sys.stderr)
        print(e.json(indent=2), file=sys.stderr)
        sys.exit(1)


# Initialize settings
settings = get_settings()


if __name__ == "__main__":
    # Example usage
    print(f"Application: {settings.app_name}")
    print(f"Environment: {settings.app_env}")
    print(f"Database: {settings.db_host}:{settings.db_port}")
