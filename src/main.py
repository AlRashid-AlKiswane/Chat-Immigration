import os
import sys
import logging
from fastapi import FastAPI

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs import setup_logging
from src.helpers import get_settings, Settings
from src.routes import upload_route, docs_to_chunks_route
from src.database import (
    get_sqlite_engine,
    init_chunks_table,
    init_user_info_table,
    init_query_response_table
)

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()

app = FastAPI(title="Immigration-Chat", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """
    FastAPI startup event handler.
    Initializes the SQLite database engine and sets up required tables.
    """
    logger.info("Starting up Ramy Chatbot API...")
    try:
        app.state.conn = get_sqlite_engine()
        init_chunks_table(conn=app.state.conn)
        init_user_info_table(conn=app.state.conn)
        init_query_response_table(conn=app.state.conn)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.critical("Failed to initialize database during startup: %s", e)
        raise RuntimeError("Startup initialization failed.") from e

# Include route modules with prefixes
app.include_router(upload_route, prefix="/upload", tags=["Upload"])
app.include_router(docs_to_chunks_route, prefix="/chunking", tags=["Document Chunking"])
