# src/chroma/client.py
import os
import sys
import logging
from typing import Optional
from chromadb import PersistentClient
from chromadb.errors import ChromaError

from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings

logger = setup_logging()
app_settings: Settings = get_settings()

def get_chroma_client() -> Optional[PersistentClient]:
    """
    Initialize and return a ChromaDB PersistentClient.
    """
    try:
        logger.info("Initializing ChromaDB PersistentClient")
        return PersistentClient(path=app_settings.CHROMA_PERSIST_DIR)
    except (ChromaError, OSError) as e:
        logger.error("Failed to initialize ChromaDB client: %s", e)
        raise
    except Exception as e:
        logger.error("Unexpected error initializing ChromaDB client: %s", e)
        raise RuntimeError(f"Failed to initialize client: {e}") from e
