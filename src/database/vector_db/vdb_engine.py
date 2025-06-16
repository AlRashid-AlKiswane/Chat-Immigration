"""
ChromaDB Client Initialization Module.

This module provides functionality to initialize and manage connections to ChromaDB,
a vector database for embeddings. It handles client configuration, error handling,
and logging for database operations.
"""

import os
import sys
import logging
from typing import Optional
from chromadb import Client
from chromadb.config import Settings as ChromaSettings
from chromadb.errors import ChromaError

from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()


def get_chroma_client() -> Optional[Client]:
    """
    Initialize and return a ChromaDB client instance.

    Returns:
        Optional[Client]: ChromaDB client object if successful, None otherwise.

    Raises:
        ChromaError: If there's an error specific to ChromaDB operations.
        OSError: If there are filesystem/path-related issues.
        RuntimeError: For other unexpected initialization errors.
    """
    try:
        logger.info("Initializing ChromaDB client")
        chroma_client = Client(ChromaSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=app_settings.chroma_persist_dir
        ))
        logger.debug("ChromaDB client initialized successfully")
        return chroma_client
    except ChromaError as e:
        logger.error("ChromaDB-specific error during initialization: %s", e)
        raise
    except OSError as e:
        logger.error("Filesystem error while initializing ChromaDB: %s", e)
        raise
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected error during ChromaDB initialization: %s", e)
        raise RuntimeError(f"Failed to initialize ChromaDB client: {e}") from e
