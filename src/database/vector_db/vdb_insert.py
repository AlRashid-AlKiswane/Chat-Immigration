"""
ChromaDB Document Operations Module.

This module provides functionality for inserting documents into ChromaDB collections
with their corresponding embeddings and IDs. It includes robust error handling
and logging for database operations.
"""

import os
import sys
import logging
from typing import List, Optional
from chromadb import Client
from chromadb.config import Settings
from chromadb.errors import ChromaError


# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()


def insert_documents(
    client: Client,
    collection_name: str,
    ids: List[str],
    embeddings: List,
    documents: List[str],
    metadatas: Optional[List[dict]] = None
) -> bool:
    """
    Insert documents with their embeddings and IDs into a ChromaDB collection.

    Args:
        client: ChromaDB client instance.
        collection_name: Name of the target collection.
        ids: List of unique document identifiers.
        embeddings: Embedding vectors (tensor or list).
        documents: List of document contents.
        metadatas: Optional list of metadata dictionaries for each document.

    Returns:
        True if insertion succeeded, False if failed.

    Raises:
        ValueError: If input lists have inconsistent lengths.
        TypeError: If input types are incorrect.
        ChromaError: For ChromaDB-specific errors.
    """
    try:
        logger.debug("Validating input formats and types")

        # Ensure ids is a list and convert all elements to strings
        if not isinstance(ids, list):
            ids = [str(ids)] if isinstance(ids, (str, int, float)) else list(ids)
        else:
            ids = [str(i) for i in ids]

        # Convert embeddings if necessary
        if hasattr(embeddings, "detach") and callable(embeddings.detach):
            embeddings = embeddings.detach().cpu().tolist()
        elif hasattr(embeddings, "tolist") and callable(embeddings.tolist):
            embeddings = embeddings.tolist()

        # Ensure embeddings is a list
        if not isinstance(embeddings, list):
            embeddings = [embeddings]

        # Ensure documents is a list
        if not isinstance(documents, list):
            documents = [documents]

        # Validate lengths
        if not all(len(lst) == len(ids) for lst in [documents, embeddings]):
            error_msg = "All input lists must have the same length"
            logger.error(error_msg)
            raise ValueError(error_msg)

        if metadatas is not None:
            if not isinstance(metadatas, list):
                metadatas = [metadatas]
            if len(metadatas) != len(ids):
                raise ValueError("Metadatas list length must match document count")

        # Ensure embeddings is a list of lists of numbers
        for i, vec in enumerate(embeddings):
            if not isinstance(vec, (list, tuple)):
                embeddings[i] = [vec]

        collection = client.get_or_create_collection(name=collection_name)

        insert_args = {
            "documents": documents,
            "ids": ids,
            "embeddings": embeddings
        }

        if metadatas is not None:
            insert_args["metadatas"] = metadatas

        logger.debug("Attempting to insert %d documents into '%s'", len(ids), collection_name)
        collection.add(**insert_args)

        logger.info("Successfully inserted %d documents", len(ids))
        return True

    except ChromaError as ce:
        logger.error("ChromaDB operation failed: %s", str(ce))
        return False
    except (ValueError, TypeError) as e:
        logger.error("%s: %s", type(e).__name__, str(e))
        raise
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected error during document insertion: %s", str(e))
        return False
