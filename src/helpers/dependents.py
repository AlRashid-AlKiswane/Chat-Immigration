"""
Database Connection and Service Retrieval Module

This module manages connections and shared resources used in a FastAPI application,
including database connections, embedding models, and vector database clients.
"""

import logging
import os
import sqlite3
import sys
from typing import Any
from fastapi import Request, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from chromadb import Client


# Attempt to set up the main directory path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs import setup_logging
from src.helpers import get_settings, Settings

# Initialize logger and application settings
logger = setup_logging()
app_settings: Settings = get_settings()

def get_db_conn(request: Request) -> sqlite3.Connection:
    """
    Retrieve the SQLite database connection from the FastAPI app state.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        sqlite3.Connection: Active SQLite connection.

    Raises:
        HTTPException: If the connection is missing or invalid.
    """
    try:
        conn = getattr(request.app.state, "conn", None)
        if not isinstance(conn, sqlite3.Connection):
            logger.error("Invalid or missing SQLite connection in app state.")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database service unavailable."
            )
        logger.debug("Successfully retrieved SQLite connection from app state.")
        return conn
    except Exception as e:
        logger.exception("Failed to retrieve SQLite connection: %s", e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while accessing the database."
        ) from e

def get_embedd(request: Request) -> Any:
    """
    Retrieve the embedding model from the FastAPI app state.

    Args:
        request (Request): The incoming FastAPI request object.

    Returns:
        Any: Embedding model instance.

    Raises:
        HTTPException: If the embedding model is not available.
    """
    try:
        embedding = getattr(request.app.state, "embedding", None)
        if embedding is None:
            logger.error("Embedding model not found in app state.")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Embedding service unavailable."
            )
        logger.debug("Successfully retrieved embedding model from app state.")
        return embedding
    except Exception as e:
        logger.exception("Failed to retrieve embedding model: %s", e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while accessing embedding model."
        ) from e

def get_vdb_client(request: Request) -> Client:
    """
    Retrieve the ChromaDB vector database client from the FastAPI app state.

    Args:
        request: The incoming FastAPI request object.

    Returns:
        Client: The ChromaDB client instance.

    Raises:
        HTTPException: If the ChromaDB client is not available.
    """
    vdb_client = getattr(request.app.state, "vdb_client", None)
    # pylint: disable=isinstance-second-argument-not-valid-type
    if not isinstance(vdb_client, Client):
        logger.error("ChromaDB client not found or invalid in application state.")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vector database service unavailable."
        )
    logger.debug("ChromaDB client retrieved successfully.")
    return vdb_client

