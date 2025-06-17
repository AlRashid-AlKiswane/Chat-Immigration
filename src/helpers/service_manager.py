"""
Service Management and Resource Access Module

This module provides centralized access to all application services and resources,
including but not limited to:

- Language Models (LLMs) - Configuration and retrieval of various AI model providers
- Vector Databases - ChromaDB client management
- Embedding Models - Access to text embedding services
- Database Connections - SQLite database connectivity
- Application Settings - Runtime configuration management

Key Responsibilities:
1. Service Initialization: Ensures required services are properly configured
2. Resource Access: Provides safe, validated access to shared resources
3. Error Handling: Standardizes error responses for service-related issues
4. Type Safety: Enforces correct service types through validation
5. Lifecycle Management: Handles service availability and state

Design Principles:
- Single Responsibility: Each function handles one specific service
- Fail Fast: Validates services immediately with clear error messages
- Loose Coupling: Services can be swapped without affecting consumers
- Observability: Comprehensive logging for debugging and monitoring

Usage:
Import and use the getter functions (get_llm, get_db_conn, etc.) in route handlers
to access configured services. All functions validate services and return
appropriate HTTP errors if services are unavailable.

Example:
    from .services import get_llm
    llm = get_llm(request)  # Handles all validation internally
"""

# Standard library imports
import logging
import os
import sys

# Special SQLite3 configuration
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Attempt to set up the main directory path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
    logging.debug("Main directory path configured: %s", MAIN_DIR)
except (ImportError, OSError) as e:
    logging.critical("Failed to set up main directory path: %s", e, exc_info=True)
    sys.exit(1)

# pylint: disable=wrong-import-position
from typing import Any
import sqlite3

# Third-party imports
from fastapi import Request, HTTPException
from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE
)
from chromadb import Client
from chromadb.api import ClientAPI

# Local application imports
from src.logs import setup_logging
from src.helpers import get_settings, Settings
from src.llms import BaseLLM


# Initialize logger and application settings
logger = setup_logging()
app_settings: Settings = get_settings()

def validate_service(service: Any, service_type: type, service_name: str) -> bool:
    """
    Validate that a service exists and is of the correct type.
    
    Args:
        service: The service instance to validate
        service_type: The expected type of the service
        service_name: Human-readable name of the service for logging
        
    Returns:
        bool: True if valid, False otherwise
    """
    if service is None:
        logger.error("%s service is None", service_name)
        return False
    if not isinstance(service, service_type):
        logger.error(
            "%s service is of type %s, expected %s",
            service_name,
            type(service).__name__,
            service_type.__name__
        )
        return False
    return True

def get_db_conn(request: Request) -> sqlite3.Connection:
    """
    Retrieve the SQLite database connection from the FastAPI app state.

    Args:
        request: The incoming FastAPI request object.

    Returns:
        sqlite3.Connection: Active SQLite connection.

    Raises:
        HTTPException: If the connection is missing or invalid (503 Service Unavailable)
    """
    try:
        conn = getattr(request.app.state, "conn", None)
        if not validate_service(conn, sqlite3.Connection, "Database"):
            raise HTTPException(
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database service unavailable."
            )
        logger.debug("Database connection retrieved successfully")
        return conn
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error retrieving database connection")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while accessing database."
        ) from e

def get_embedd(request: Request) -> Any:
    """
    Retrieve the embedding model from the FastAPI app state.

    Args:
        request: The incoming FastAPI request object.

    Returns:
        Any: Initialized embedding model instance.

    Raises:
        HTTPException: If the embedding model is not available (503 Service Unavailable)
    """
    try:
        embedding = getattr(request.app.state, "embedding", None)
        if embedding is None:
            logger.error("Embedding model not initialized")
            raise HTTPException(
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                detail="Embedding service unavailable."
            )
        logger.debug("Embedding model retrieved successfully")
        return embedding
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error retrieving embedding model")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while accessing embedding service."
        ) from e

def get_vdb_client(request: Request) -> ClientAPI:
    """
    Retrieve the ChromaDB vector database client from the FastAPI app state.

    Args:
        request: The incoming FastAPI request object.

    Returns:
        ClientAPI: The ChromaDB client instance.

    Raises:
        HTTPException: If the ChromaDB client is not available (503 Service Unavailable)
    """
    try:
        vdb_client = getattr(request.app.state, "vdb_client", None)
        if not validate_service(vdb_client, Client, "Vector Database"):
            raise HTTPException(
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vector database service unavailable."
            )
        logger.debug("Vector database client retrieved successfully")
        return vdb_client
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error retrieving vector database client")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while accessing vector database."
        ) from e

def get_llm(request: Request) -> BaseLLM:
    """
    Retrieve the configured LLM instance from the FastAPI app state.

    Args:
        request: The incoming FastAPI request object.

    Returns:
        BaseLLM: Initialized LLM instance.

    Raises:
        HTTPException: If the LLM is not configured (503 Service Unavailable)
                     or if there's an internal error (500 Internal Server Error)
    """
    try:
        llm = getattr(request.app.state, "llm", None)
        if not validate_service(llm, BaseLLM, "Language Model"):
            raise HTTPException(
                status_code=HTTP_503_SERVICE_UNAVAILABLE,
                detail="Language model service unavailable. Please configure an LLM first."
            )

        logger.debug("LLM instance retrieved successfully: %s", llm.get_model_info())
        return llm
    except HTTPException:
        raise
    except AttributeError as e:
        logger.error("LLM instance missing required methods: %s", str(e))
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Language model configuration error."
        ) from e
    except Exception as e:
        logger.exception("Unexpected error retrieving LLM instance")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while accessing language model."
        ) from e
