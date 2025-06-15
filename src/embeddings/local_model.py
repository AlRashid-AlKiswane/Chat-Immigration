"""
Sentence Transformer Embedding Module.

This module provides a wrapper class for generating text embeddings using
SentenceTransformer models. It handles model initialization, text embedding,
and includes error handling and logging capabilities.
"""

import logging
import os
import sys
from typing import List, Union, Optional
from sentence_transformers import SentenceTransformer # type: ignore

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs import setup_logging
from src.helpers import get_settings, Settings

# Initialize application settings and logger
logger = setup_logging()
app_settings: Settings = get_settings()


class EmbeddingModel:
    """
    Handles SentenceTransformer-based embeddings.

    This class provides functionality to:
    - Load a pre-trained SentenceTransformer model
    - Generate embeddings for text inputs
    - Handle errors during embedding generation
    - Log embedding operations

    Args:
        model_name: Name of the SentenceTransformer model to load.
                   If None, uses the model from app settings.
    """

    def __init__(self, model_name: Optional[str] = None):
        """Initialize the embedding model."""
        self.model_name = model_name or app_settings.EMBEDDING_MODEL
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model '%s' initialized.", self.model_name)
        except Exception as e:
            logger.error("Failed to load embedding model '%s': %s", self.model_name, e)
            raise

    def embed(
        self,
        text: Union[str, List[str]],
        convert_to_tensor: bool = True,
        normalize_embeddings: bool = False
    ) -> Optional[Union[List[float], List[List[float]]]]:
        """
        Generate embeddings for a given string or list of strings.

        Args:
            text: Single string or list of strings to embed.
            convert_to_tensor: Whether to return embeddings as tensors.
            normalize_embeddings: Whether to normalize the embeddings.

        Returns:
            Embeddings as a list or tensor, or None on error.

        Raises:
            ValueError: If input text is empty or invalid.
            Exception: For other embedding generation errors.
        """
        if not text:
            logger.error("Empty text provided for embedding.")
            raise ValueError("Input text cannot be empty.")

        try:
            embedding = self.model.encode(
                text,
                convert_to_tensor=convert_to_tensor,
                normalize_embeddings=normalize_embeddings
            )

            preview_text = text if isinstance(text, str) else text[0]
            logger.info("Generated embedding for text: '%.30s...'", preview_text)
            return embedding
        # pylint: disable=broad-exception-caught
        except Exception as e:
            logger.error("Error generating embedding: %s", e)
            return None

    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.

        Returns:
            Dictionary containing model information.
        """
        return {
            "model_name": self.model_name,
            "max_seq_length": self.model.max_seq_length,
            "embedding_dimension": self.model.get_sentence_embedding_dimension()
        }
