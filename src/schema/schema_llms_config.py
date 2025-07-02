

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional


class ModelInfo(BaseModel):
    """Schema for model metadata information"""
    model_name: Optional[str] = Field(
        None, description="Identifier for the model")
    provider: str = Field(...,
                          description="Service or framework providing the model")


class GenerationParameters(BaseModel):
    """Schema for common LLM generation parameters"""
    temperature: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="Controls randomness. Lower = more deterministic"
    )
    max_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum number of tokens to generate"
    )
    top_p: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling probability threshold"
    )
    top_k: Optional[int] = Field(
        default=None,
        ge=1,
        description="Number of highest probability tokens to consider"
    )
    max_input_tokens: Optional[int] = Field(
        default=None,
        ge=1,
        description="Maximum number of input tokens allowed (context window size)"
    )
