"""
Application configuration settings loaded from environment variables.

This module provides a Settings class that loads configuration from:
1. .env file
2. Environment variables
3. Default values
"""

import sys
from typing import List, Optional
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings configuration.

    Uses Pydantic for validation and type conversion.
    Environment variables take precedence over .env file values.
    """

    FILE_TYPES: List[str] = Field(..., env="FILE_TYPES")
    DOC_LOCATION_SAVE: str = Field(..., env="DOC_LOCATION_SAVE")
    CHUNKS_SIZE: int = Field(..., env="CHUNKS_SIZE")
    CHUNKS_OVERLAP: int = Field(..., env="CHUNKS_OVERLAB")

    EMBEDDING_MODEL: str = Field(..., env="EMBEDDING_MODEL")

    OPENAI_APIK: Optional[str] = Field(None, env="OPENAI_APIK")
    OPENAI_MODEL: Optional[str] = Field(None, env="OPENAI_MODEL")

    GEMINI_APIK: Optional[str] = Field(None, env="GEMINI_APIK")
    GEMINI_MODEL: Optional[str] = Field(None, env="GEMINI_MODEL")

    COHERE_APIK: Optional[str] = Field(None, env="COHERE_APIK")
    COHERE_MODEL: Optional[str] = Field(None, env="COHERE_MODEL")

    HUGGINGFACE_MODEL: Optional[str] = Field(None, env="HUGGINGFACE_MODEL")
    HUGGINGFACE_APIK: Optional[str] = Field(None, env="HUGGINGFACE_APIK")

    DEEPSEEK_APIK: Optional[str] = Field(None, env="DEEPSEEK_APIK")
    DEEPSEEK_MODEL: Optional[str] = Field(None, env="DEEPSEEK_MODEL")
    DEEPSEEK_API_BASE: Optional[str] = Field(None, env="DEEPSEEK_API_BASE")


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
    # Example usage for debugging
    print(f"Doc Save Location: {settings.DOC_LOCATION_SAVE}")
    print(f"OpenAI Model: {settings.OPENAI_MODEL}")
    print(f"HuggingFace Model: {settings.HUGGINGFACE_MODEL}")
