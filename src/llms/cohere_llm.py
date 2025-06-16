"""
Cohere LLM Implementation Module.

This module provides a concrete implementation of the BaseLLM abstract class
for interacting with Cohere's language models using the Cohere API.
It handles model initialization, prompt processing, and structured error handling.
"""

import logging
import os
import sys
from typing import Optional, Dict, Any
import cohere

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs import setup_logging
from src.helpers import get_settings, Settings
from .__abc_llm import BaseLLM

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()

class CohereLLM(BaseLLM):
    """
    Cohere LLM client implementing the BaseLLM interface.

    Handles text generation and model metadata retrieval using Cohere API.
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        """Initialize the Cohere LLM with optional custom model name."""
        self.model_name = model_name or app_settings.COHERE_MODEL
        self.api_key = app_settings.COHERE_APIK
        self.client = cohere.Client(api_key=self.api_key)

        logger.info("Initialized Cohere LLM with model: %s", self.model_name)

    def generate_response(
        self,
        prompt: str,
        **kwargs: Any
    ) -> str:
        """
        Generate a response from the Cohere language model.

        Args:
            prompt: The prompt string to send.
            **kwargs: Model-specific parameters (e.g., temperature, max_tokens).

        Returns:
            Generated response as a string.

        Raises:
            RuntimeError: If Cohere API call fails.
        """
        if not prompt:
            logger.error("Empty prompt provided to Cohere LLM.")
            raise ValueError("Prompt must not be empty.")

        try:
            response = self.client.chat(
                model=self.model_name,
                message=prompt,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 256),
                stream=False
            )
            reply = response.text.strip()
            logger.info("Cohere response generated successfully.")
            return reply

        except Exception as e:
            logger.error("Cohere API call failed: %s", e)
            raise RuntimeError(f"Cohere LLM generation failed: {e}") from e

    def get_model_info(self) -> Dict[str, Any]:
        """
        Return metadata about the Cohere model.

        Returns:
            Dictionary with model details.
        """
        return {
            "model_name": self.model_name,
            "provider": "Cohere",
            "capabilities": {
                "chat": True,
                "streaming": False,
                "temperature_control": True,
                "max_tokens": True
            },
            "parameters": {
                "temperature": "float [0.0 - 1.0]",
                "max_tokens": "int"
            }
        }
