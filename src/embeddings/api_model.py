"""
OpenAI Embedding Generation Module.

This module provides a wrapper class for generating text embeddings using OpenAI's API.
It handles API communication, error management, and includes support for batch processing
of text inputs with proper chunking for large requests.
"""

import logging
import os
import sys
from typing import List, Union, Optional
from openai import OpenAI, OpenAIError

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


class OpenAIEmbeddingModel:
    """
    A wrapper class for generating text embeddings using OpenAI's API.

    This class handles:
    - API client initialization
    - Batch processing of text inputs
    - Error handling and logging
    - Configuration management

    Attributes:
        api_key (str): OpenAI API key
        model_name (str): Name of the embedding model to use
        max_batch_size (int): Maximum number of texts to process in a single batch
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize the OpenAI embedding model wrapper.

        Args:
            api_key: OpenAI API key. If not provided, uses the key from app settings.
            model_name: Name of the embedding model. If not provided,
            uses the model from app settings.

        Raises:
            ValueError: If API key or model name are missing or invalid.
        """
        self.api_key = api_key or app_settings.openai_api_key
        self.model_name = model_name or app_settings.openai_embedding_model
        self.max_batch_size = 2048  # OpenAI's maximum batch size for embeddings

        if not self.api_key:
            logger.error("OpenAI API key is missing.")
            raise ValueError("OpenAI API key must be provided.")

        if not self.model_name:
            logger.error("OpenAI embedding model name is missing.")
            raise ValueError("OpenAI embedding model name must be provided.")

        logger.info("OpenAIEmbeddingModel initialized with model: %s", self.model_name)

    def embed_texts(
        self,
        texts: Union[List[str], str],
        batch_size: Optional[int] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for the input text(s).

        Args:
            texts: A single string or a list of strings to generate embeddings for.
            batch_size: Number of texts to process in each batch. If None, uses class default.

        Returns:
            A list of embedding vectors (list of floats) for each input text.

        Raises:
            ValueError: If input texts are empty or invalid.
            OpenAIError: If there's an error with the OpenAI API request.
            Exception: For other unexpected errors.
        """
        if not texts:
            logger.error("No texts provided for embedding.")
            raise ValueError("Input texts cannot be empty.")

        if isinstance(texts, str):
            texts = [texts]

        batch_size = batch_size or self.max_batch_size
        embeddings = []
        client = OpenAI(api_key=self.api_key)

        try:
            # Process texts in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                logger.debug("Processing batch %d-%d of %d texts",
                           i, min(i + batch_size, len(texts)), len(texts))

                try:
                    response = client.embeddings.create(
                        input=batch,
                        model=self.model_name
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)
                except OpenAIError as oe:
                    logger.error(
                        "OpenAI API error for batch %d-%d: %s",
                        i, i + batch_size, str(oe)
                    )
                    raise
                except Exception as e:
                    logger.error(
                        "Unexpected error processing batch %d-%d: %s",
                        i, i + batch_size, str(e)
                    )
                    raise

            logger.info(
                "Successfully generated embeddings for %d texts across %d batches",
                len(texts),
                (len(texts) // batch_size) + 1
            )
            return embeddings

        except Exception as e:
            logger.error("Failed to generate embeddings: %s", str(e))
            raise
