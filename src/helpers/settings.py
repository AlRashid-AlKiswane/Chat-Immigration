"""
Application configuration settings loaded from environment variables.

This module provides a Settings class that loads configuration from:
1. .env file (not committed to version control)
2. Environment variables
3. Default values (for non-sensitive settings)
"""

import sys
from pathlib import Path
from typing import List, Optional
from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings configuration with proper security measures.

    Note:
    - Sensitive credentials are stored as SecretStr
    - Required database paths are validated
    - All API keys are optional for local development
    """

    # Database Configuration
    SQLITE_DB: str = Field(
        "sqlite:///./database/data.db",
        env="SQLITE_DB",
        description="SQLite database connection string"
    )
    
    # Document Processing
    FILE_TYPES: List[str] = Field(
        ["txt", "pdf"],
        env="FILE_TYPES",
        description="Supported file extensions for document processing"
    )
    DOC_LOCATION_SAVE: Path = Field(
        Path("./assets/docs"),
        env="DOC_LOCATION_SAVE",
        description="Directory to store uploaded documents"
    )
    CHUNKS_SIZE: int = Field(
        500,
        gt=100,
        lt=2000,
        env="CHUNKS_SIZE",
        description="Size of text chunks for processing (100-2000 chars)"
    )
    CHUNKS_OVERLAP: int = Field(
        30,
        ge=0,
        lt=100,
        env="CHUNKS_OVERLAP",
        description="Overlap between chunks (0-100 chars)"
    )

    # Embedding Model
    EMBEDDING_MODEL: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2",
        env="EMBEDDING_MODEL",
        description="Default embedding model"
    )

    # API Configurations (all optional)
    OPENAI_API_KEY: Optional[SecretStr] = Field(
        None,
        env="OPENAI_API_KEY",
        description="OpenAI API key (keep secret!)"
    )
    OPENAI_MODEL: Optional[str] = Field(
        None,
        env="OPENAI_MODEL",
        description="OpenAI model name"
    )

    # [Similar SecretStr patterns for other APIs...]
    GEMINI_API_KEY: Optional[SecretStr] = Field(None, env="GEMINI_API_KEY")
    COHERE_API_KEY: Optional[SecretStr] = Field(None, env="COHERE_API_KEY")
    HUGGINGFACE_API_KEY: Optional[SecretStr] = Field(None, env="HUGGINGFACE_API_KEY")
    DEEPSEEK_API_KEY: Optional[SecretStr] = Field(None, env="DEEPSEEK_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        secrets_dir="/run/secrets"  # For Docker secrets
    )


def get_settings() -> Settings:
    """
    Safely initialize application settings with proper error handling.

    Returns:
        Settings: Configured settings instance

    Raises:
        SystemExit: If configuration is invalid
    """
    try:
        settings = Settings()
        
        # Ensure document directory exists
        settings.DOC_LOCATION_SAVE.mkdir(exist_ok=True, parents=True)
        
        return settings
        
    except ValidationError as e:
        print("Configuration error:", file=sys.stderr)
        print(e.json(indent=2), file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Filesystem error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Safe debugging - never prints secrets
    settings = get_settings()
    print("=== Safe Configuration Debug ===")
    print(f"Database: {settings.SQLITE_DB}")
    print(f"Document Location: {settings.DOC_LOCATION_SAVE}")
    print(f"Chunk Size: {settings.CHUNKS_SIZE}")
    
    # Example of accessing a secret (would show as '***********' in logs)
    if settings.OPENAI_API_KEY:
        print("OpenAI configured (key hidden)")