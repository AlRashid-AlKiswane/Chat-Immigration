"""
Main entry point for the Immigration Chatbot FastAPI application.

Handles application startup and shutdown events, sets up SQLite database tables,
and includes routes for file upload and document chunking.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

# Setup project base path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("[Startup] Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs import setup_logging
from src.helpers import get_settings, Settings

from src.routes import (upload_route,
                        docs_to_chunks_route
)
from src.database import (
    get_sqlite_engine,
    init_chunks_table,
    init_user_info_table,
    init_query_response_table
)

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context to handle startup and shutdown events.
    Initializes and tears down database resources.
    """
    logger.info("[Startup] Starting up Immigration Chatbot API...")
    try:
        app.state.conn = get_sqlite_engine()
        init_chunks_table(conn=app.state.conn)
        init_user_info_table(conn=app.state.conn)
        init_query_response_table(conn=app.state.conn)
        logger.info("[Startup] Database tables initialized successfully.")
    except Exception as e:
        logger.critical("[Startup] Failed to initialize database: %s", e)
        raise RuntimeError("Startup initialization failed.") from e

    yield

    logger.info("[Shutdown] Cleaning up Immigration Chatbot API resources...")
    try:
        conn = app.state.conn
        if conn:
            conn.close()
            logger.info("[Shutdown] Database connection closed.")
    except (RuntimeError, IOError) as exc:
        logger.error("[Shutdown] Error during shutdown cleanup: %s", exc)

# Create FastAPI app with lifespan
app = FastAPI(title="Immigration Chatbot", version="1.0.0", lifespan=lifespan)

# Include route modules with prefixes
app.include_router(upload_route, prefix="/upload", tags=["Upload"])
app.include_router(docs_to_chunks_route, prefix="/chunking", tags=["Document Chunking"])
