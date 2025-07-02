"""
DeepSeek LLM Implementation Module.

This module provides a concrete implementation of the BaseLLM abstract class
for interacting with DeepSeek's language models using the OpenAI-compatible API.
"""

import logging
import os
import sys
from typing import Optional, Dict, Any
from openai import OpenAI

try:
    MAIN_DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs import setup_logging
from src.helpers import get_settings, Settings
from src.llms.abc_llm import BaseLLM

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()


class DeepSeekLLM(BaseLLM):
    """
    DeepSeek LLM client implementing the BaseLLM interface.

    Uses the OpenAI SDK to interact with DeepSeek's API endpoint.
    Handles text generation and model metadata retrieval.
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        """Initialize the DeepSeek LLM with optional custom model name."""
        self.model_name = model_name or app_settings.DEEPSEEK_MODEL
        self.api_key = app_settings.DEEPSEEK_APIK
        self.base_url = app_settings.DEEPSEEK_API_BASE or "https://api.deepseek.com"

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        logger.info("Initialized DeepSeek LLM with model: %s", self.model_name)

    def generate_response(
        self,
        prompt: str,
        **kwargs: Any
    ) -> str:
        """
        Generate a response from the DeepSeek language model.

        Args:
            prompt: The prompt string to send.
            **kwargs: Model-specific parameters:
                - temperature: float (default 0.7)
                - max_tokens: int (default 1024)
                - top_p: float (default 1.0)
                - stream: bool (default False)
                - frequency_penalty: float (default 0.0)
                - presence_penalty: float (default 0.0)

        Returns:
            Generated response as a string.

        Raises:
            RuntimeError: If API call fails.
            ValueError: If prompt is empty.
        """
        if not prompt:
            logger.error("Empty prompt provided to DeepSeek LLM")
            raise ValueError("Prompt must not be empty")

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1024),
                max_input_tokens=kwargs.get("max_input_tokens", 256),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
                stream=kwargs.get("stream", False)
            )

            content = response.choices[0].message.content
            logger.info("Successfully generated response from DeepSeek LLM")
            return content

        except Exception as e:
            logger.error("DeepSeek API call failed: %s", str(e))
            raise RuntimeError(f"DeepSeek LLM generation failed: {e}") from e

    def get_model_info(self) -> Dict[str, Any]:
        """
        Return metadata about the DeepSeek model.

        Returns:
            Dictionary with model details including:
            - model_name: str
            - provider: str
            - capabilities: dict
            - parameters: dict
        """
        return {
            "model_name": self.model_name,
            "provider": "DeepSeek",
            "capabilities": {
                "chat": True,
                "streaming": True,
                "temperature_control": True,
                "max_tokens": True,
                "context_window": 128000  # Update with actual context size
            },
            "parameters": {
                "temperature": "float [0.0 - 2.0]",
                "max_tokens": "int [1 - 4096]",  # Update with actual limits
                "top_p": "float [0.0 - 1.0]",
                "frequency_penalty": "float [0.0 - 2.0]",
                "presence_penalty": "float [0.0 - 2.0]",
                "stream": "boolean"
            }
        }


if __name__ == "__main__":
    model = DeepSeekLLM()
    response = model.generate_response(
        prompt="What is RNN in machine learning?")
    print(response)
