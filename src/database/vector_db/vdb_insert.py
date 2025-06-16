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
    embeddings: List[List[float]],
    documents: List[str],
    metadatas: Optional[List[dict]] = None
) -> bool:
    """
    Insert documents with their embeddings and IDs into a ChromaDB collection.

    Args:
        client: ChromaDB client instance.
        collection_name: Name of the target collection.
        ids: List of unique document identifiers.
        embeddings: List of embedding vectors corresponding to documents.
        documents: List of document contents.
        metadatas: Optional list of metadata dictionaries for each document.

    Returns:
        True if insertion succeeded, False if failed.

    Raises:
        ValueError: If input lists have inconsistent lengths.
        TypeError: If input types are incorrect.
        ChromaError: For ChromaDB-specific errors.
    """
    # Input validation
    if not all(len(lst) == len(ids) for lst in [documents, embeddings]):
        error_msg = "All input lists must have the same length"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if metadatas is not None and len(metadatas) != len(ids):
        error_msg = "Metadatas list length must match documents list"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        logger.info("Inserting %d documents into collection '%s'", 
                   len(documents), collection_name)

        collection = client.get_or_create_collection(name=collection_name)

        insert_args = {
            "documents": documents,
            "ids": ids,
            "embeddings": embeddings
        }

        if metadatas is not None:
            insert_args["metadatas"] = metadatas

        collection.add(**insert_args)

        logger.debug("Successfully inserted %d documents", len(documents))
        return True

    except ChromaError as ce:
        logger.error("ChromaDB operation failed: %s", str(ce))
        return False
    except ValueError as ve:
        logger.error("Invalid input value: %s", str(ve))
        raise
    except TypeError as te:
        logger.error("Type error during insertion: %s", str(te))
        raise
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected error during document insertion: %s", str(e))
        return False

