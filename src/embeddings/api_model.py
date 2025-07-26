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
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.infra import setup_logging
from src.helpers import get_settings, Settings
from src.enums import OPenAPIEmbeddingMsg

# Initialize application settings and logger
logger = setup_logging(name="OPENAI-EMBEDDING")
app_settings: Settings = get_settings()


# pylint: disable=too-few-public-methods
# pylint: disable=logging-not-lazy
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

    def __init__(self):
        """
        Initialize the OpenAI embedding model wrapper.

        Args:
            api_key: OpenAI API key. If not provided, uses the key from app settings.
            model_name: Name of the embedding model. If not provided,
            uses the model from app settings.

        Raises:
            ValueError: If API key or model name are missing or invalid.
        """
        self.api_key = (app_settings.OPENAI_APIK.get_secret_value()
                        if app_settings.OPENAI_APIK
                        else None)
        self.model_name = app_settings.EMBEDDING_OPENAI
        self.max_batch_size = 2048  # OpenAI's maximum batch size for embeddings

        if not self.api_key:
            logger.error(OPenAPIEmbeddingMsg.INVALID_API_KEY.value)
            raise ValueError(OPenAPIEmbeddingMsg.INVALID_API_KEY.value)

        if not self.model_name:
            logger.error(OPenAPIEmbeddingMsg.INVALID_MODEL_NAME.value)
            raise ValueError(OPenAPIEmbeddingMsg.INVALID_MODEL_NAME.value)

        logger.info(OPenAPIEmbeddingMsg.MODEL_INIT_COMPLETE.value % (self.model_name, self.max_batch_size))

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
            logger.error(OPenAPIEmbeddingMsg.EMPTY_INPUT.value)
            raise ValueError(OPenAPIEmbeddingMsg.EMPTY_INPUT.value)

        if isinstance(texts, str):
            texts = [texts]

        batch_size = batch_size or self.max_batch_size
        embeddings = []
        client = OpenAI(api_key=self.api_key)

        try:
            # Process texts in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]

                try:
                    response = client.embeddings.create(
                        input=batch,
                        model=self.model_name
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)
                except OpenAIError as oe:
                    logger.error(
                        OPenAPIEmbeddingMsg.OPENAI_BATCH_ERROR.value %
                        (i, i + batch_size, str(oe))
                    )
                    raise
                except Exception as e:
                    logger.error(
                       OPenAPIEmbeddingMsg.UNEXPECTED_ERROR.value %
                        (i, i + batch_size, str(e))
                    )
                    raise
            return embeddings

        except Exception as e:
            logger.error(OPenAPIEmbeddingMsg.GENERATION_FAILED.value % str(e))
            raise

if __name__ == "__main__":
    embedd = OpenAIEmbeddingModel()
    embeddings_vectore = embedd.embed_texts(texts="How are u rashid, u can help me")
    print(embeddings_vectore)
