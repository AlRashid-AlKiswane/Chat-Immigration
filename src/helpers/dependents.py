"""
Database Connection Management Module

This module provides functionality for managing SQLite database connections
in a FastAPI application, including connection retrieval and error handling.
"""

import logging
import os
import sqlite3
import sys
from fastapi import Request, HTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs import setup_logging
from src.helpers import get_settings, Settings

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()

def get_db_conn(request: Request) -> sqlite3.Connection:
    """
    Retrieve the SQLite database connection from the FastAPI app state.

    Args:
        request: The incoming FastAPI request object.

    Returns:
        The active database connection.

    Raises:
        HTTPException: If the database connection is not available or invalid.
    """
    try:
        conn = getattr(request.app.state, "conn", None)
        if not isinstance(conn, sqlite3.Connection):
            logger.error("Invalid database connection instance in app state")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database service unavailable"
            )
        return conn
    except AttributeError as e:
        logger.error("Database connection not found in application state: %s", e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database service unavailable"
        ) from e
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("Unexpected error retrieving database connection")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from e
