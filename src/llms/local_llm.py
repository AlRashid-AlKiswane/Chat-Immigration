"""
HuggingFace LLM Implementation Module.

This module provides a concrete implementation of the BaseLLM abstract class
for interacting with locally hosted HuggingFace transformer models.
It handles model loading, prompt processing, and structured error handling.
"""

import logging
import os
import sys
from typing import Optional, Dict, Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import login

try:
    MAIN_DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.infra import setup_logging
from src.helpers import get_settings, Settings
from src.llms.abc_llm import BaseLLM

# Initialize logger and settings
logger = setup_logging(name="LOCAL-PROVIDER")
app_settings: Settings = get_settings()


class HuggingFaceLLM(BaseLLM):
    """
    HuggingFace LLM client implementing the BaseLLM interface.

    Handles text generation using a local HuggingFace transformer model.
    """

    def __init__(self, model_name: Optional[str] = None) -> None:
        """Initialize the HuggingFace LLM with optional custom model name."""
        self.model_name = model_name or app_settings.HUGGINGFACE_MODEL
        try:
            login(token=app_settings.HUGGINGFACE_APIK)
            logging.info("Successfully logged into HuggingFace.")

        # pylint: disable=broad-exception-caught
        except Exception as e:
            logging.error("Failed to log into HuggingFace: %s", e)

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)

            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
                logger.info("Model loaded to GPU.")
            else:
                logger.info("Model loaded to CPU.")

            logger.info(
                "Initialized HuggingFace LLM with model: %s", self.model_name)
        except Exception as e:
            logger.error(
                "Failed to load HuggingFace model '%s': %s", self.model_name, e)
            raise RuntimeError(f"Failed to load HuggingFace model: {e}") from e

    def generate_response(
        self,
        prompt: str,
        **kwargs: Any
    ) -> str:
        """
        Generate a response from the HuggingFace language model.

        Args:
            prompt: The input text prompt.
            **kwargs: Model-specific generation parameters.

        Returns:
            Generated response as a string.

        Raises:
            RuntimeError: If generation fails.
        """
        if not prompt:
            logger.error("Empty prompt provided to HuggingFace LLM.")
            raise ValueError("Prompt must not be empty.")

        try:
            inputs = self.tokenizer(prompt, return_tensors="pt")
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            outputs = self.model.generate(
                **inputs,
                max_new_tokens=kwargs.get("max_tokens", 256),
                max_input_tokens=kwargs.get("max_input_tokens", 256),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 1.0),
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
            response = self.tokenizer.decode(
                outputs[0], skip_special_tokens=True)

            # Strip input prompt if model repeats it in output
            reply = response[len(prompt):].strip() if response.startswith(
                prompt) else response.strip()

            logger.info("HuggingFace response generated successfully.")
            return reply

        except Exception as e:
            logger.error("HuggingFace model generation failed: %s", e)
            raise RuntimeError(f"HuggingFace generation failed: {e}") from e

    def get_model_info(self) -> Dict[str, Any]:
        """
        Return metadata about the HuggingFace model.

        Returns:
            Dictionary with model details.
        """
        return {
            "model_name": self.model_name,
            "provider": "HuggingFace",
            "capabilities": {
                # Unless using a conversational model like ChatGLM, DialoGPT, etc.
                "chat": False,
                "streaming": False,
                "temperature_control": True,
                "max_tokens": True
            },
            "parameters": {
                "temperature": "float [0.0 - 1.0]",
                "max_tokens": "int",
                "top_p": "float [0.0 - 1.0]"
            }
        }


if __name__ == "__main__":

    model = HuggingFaceLLM()
    response = model.generate_response(
        prompt="What is the RNN in machine learning")
    print(response)
