"""
Embedding Model Factory Module.

This module provides a factory function to instantiate and return different types of 
embedding models based on the specified model name. It supports both OpenAI and 
local HuggingFace embedding models with proper error handling and logging.
"""

import os
import sys
import logging
from typing import Union

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("[Startup] Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs import setup_logging
from src.embeddings import OpenAIEmbeddingModel, HuggingFaceModel


logger = setup_logging()

async def run_embedding_model(
        model_name: str = "OPENAI"
    ) -> Union[OpenAIEmbeddingModel, HuggingFaceModel]:
    """
    Factory function to instantiate and return an embedding model based on the specified type.

    Args:
        model_name: A string specifying which embedding model to instantiate. 
                   Valid values are "OPENAI" (default) or "LOCAL".

    Returns:
        An instance of the requested embedding model (OpenAIEmbeddingModel or HuggingFaceModel).

    Raises:
        ValueError: If an invalid model_name is provided.
        ImportError: If required dependencies for the selected model are not available.
        RuntimeError: If model initialization fails for any reason.

    Examples:
        >>> # For OpenAI embeddings
        >>> model = await run_embedding_model("OPENAI")
        
        >>> # For local HuggingFace embeddings
        >>> model = await run_embedding_model("LOCAL")
    """
    try:
        logger.debug(f"Attempting to initialize embedding model: {model_name}")

        model = None
        if model_name.upper() == "OPENAI":
            try:
                model = OpenAIEmbeddingModel()
                logger.info("Successfully initialized OpenAI embedding model")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI embedding model: {str(e)}")
                raise RuntimeError(f"OpenAI embedding model initialization failed: {e}") from e

        elif model_name.upper() == "LOCAL":
            try:
                model = HuggingFaceModel()
                logger.info("Successfully initialized local HuggingFace embedding model")
            except ImportError as e:
                logger.error(f"HuggingFace dependencies not available: {str(e)}")
                raise ImportError("HuggingFace dependencies not installed. "
                                "Please install required packages.") from e
            except Exception as e:
                logger.error(f"Failed to initialize HuggingFace model: {str(e)}")
                raise RuntimeError(f"HuggingFace model initialization failed: {e}") from e

        else:
            error_msg = f"Invalid model name: {model_name}. Valid options are 'OPENAI' or 'LOCAL'"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return model

    except Exception as e:
        logger.critical(f"Unexpected error in run_embedding_model: {str(e)}")
        raise RuntimeError(f"Embedding model factory failed: {e}") from e
