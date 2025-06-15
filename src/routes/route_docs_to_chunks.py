"""
Document Chunking API Module

Provides FastAPI endpoint for processing documents into chunks and storing them in database.
Handles document loading, text chunking, and database operations with comprehensive error handling.
"""

import os
import sqlite3
import sys
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings, get_db_conn
from src.schema import ChunkData, ChunksRequest
from src.database import clear_table, insert_chunks
from src.controllers import load_and_chunk
from src.utils import prepare_chunks_for_insertion

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()

docs_to_chunks_route = APIRouter()

@docs_to_chunks_route.post("/docs_to_chunks")
async def docs_to_chunks(
    body: ChunksRequest,
    conn: sqlite3.Connection = Depends(get_db_conn)
) -> JSONResponse:
    """
    Process documents into chunks and store in database.

    Args:
        body: Request containing file path and reset flag
        conn: Database connection dependency

    Returns:
        JSON response with operation status

    Raises:
        HTTPException: For various error conditions
    """
    file_path = body.file_path
    do_reset = body.do_rest

    logger.info("Starting chunking process for: %s", file_path or "[ALL DOCUMENTS]")

    try:
        if do_reset == 1:
            clear_table(conn=conn, table_name="chunks")
            logger.info("Cleared 'chunks' table as requested")

        data: ChunkData = load_and_chunk(file_path=file_path)

        if not data or len(data) == 0:
            msg = "No valid documents found to process"
            logger.warning(msg)
            return JSONResponse(
                content={"status": "error", "message": msg},
                status_code=404
            )
        data = prepare_chunks_for_insertion(data=data)
        insert_chunks(conn=conn, chunks_data=data)
        logger.info("Inserted %d chunks into database", len(data))

        return JSONResponse(
            content={
                "status": "success",
                "inserted_chunks": len(data),
                "documents": data
            },
            status_code=200
        )

    except ValueError as ve:
        logger.error("Validation error: %s", ve)
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        ) from ve

    except sqlite3.DatabaseError as dbe:
        logger.error("Database error: %s", dbe)
        raise HTTPException(
            status_code=500,
            detail="Database operation failed"
        ) from dbe

    except Exception as e:  # pylint: disable=broad-except
        logger.exception("Unexpected error: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        ) from e
