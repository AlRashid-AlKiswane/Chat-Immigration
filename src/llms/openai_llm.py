"""
OpenAI LLM Implementation Module.

This module provides a concrete implementation of the BaseLLM abstract class
for interacting with OpenAI's language models using the OpenAI API.
It handles model initialization, prompt processing, and structured error handling.
"""


import logging
import os
import sys
from typing import Optional, Dict, Any
import openai

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
from src.enums.value_enums import ModelProvider
# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()


class OpenAILLM(BaseLLM):
    """
    OpneAI LLM client implementing the BaseLLM interface.

    Handles text generation and model metdata retrieveal useing OpenAI API.
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        """Initialize the OpenAI LLM with optinal custom model name."""
        self.model_name = model_name or app_settings.OPENAI_MODEL
        self.api_key = (app_settings.OPENAI_APIK.get_secret_value()
                        if app_settings.OPENAI_APIK
                        else None)
        self.client = openai.OpenAI(api_key=self.api_key)

        logger.info("Initialized OpenAI LLM with model: %s", self.model_name)

    def generate_response(
        self,
        prompt: str,
        **kwargs: Any
    ) -> str:
        """
        Generate a response from the OpenAI language model.

        Args:
            prompt: The prompt string to send.
            chat_history: List of messages for conversation context.
            **kwargs: Model-specific parameters (e.g., temperature, max_tokens).

        Returns:
            Generated response as a string.

        Raises:
            RuntimeError: If OpenAI API call fails.
        """
        if not prompt:
            logger.error("Empty prompt provided to OpenAI LLM.")
            raise ValueError("Prompt must not be empty.")
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 256), #both input and output
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
            )
            reply = response.choices[0].message.content.strip()
            logger.info("OpenAI response generated successfully.")
            return reply

        except Exception as e:
            logger.error("OpenAI API call failed: %s", e)
            raise RuntimeError(f"OpenAI LLM generation failed: {e}") from e

    def get_model_info(self) -> Dict[str, Any]:
        """
        Return metadata about the OpenAI model.

        Returns:
            Dictionary with model details.
        """
        return {
            "model_name": self.model_name,
            "provider": ModelProvider.OPENAI.value,
            "capabilities": {
                "chat": True,
                "streaming": True,
                "temperature_control": True,
                "max_tokens": True
            },
            "parameters": {
                "temperature": "float [0.0 - 1.0]",
                "max_tokens": "int",
                "top_p": "float [0.0 - 1.0]",
                "frequency_penalty": "float",
                "presence_penalty": "float"
            }
        }


if __name__ == "__main__":
    model = OpenAILLM()
    response = model.generate_response(prompt="Hello how are you")
    print(response)
