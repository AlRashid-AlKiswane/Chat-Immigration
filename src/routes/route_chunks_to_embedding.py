"""
Embedding Route Module

This module provides an API endpoint for generating vector embeddings
 from text chunks stored in a SQLite database.
The embedding is performed using the OpenAIEmbeddingModel.
 It ensures proper logging, error handling, and response formatting.
"""

# pylint: disable=wrong-import-position
import logging
import os
import sys

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from sqlite3 import Connection  # Ensure Pylint recognizes it as a valid type
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from chromadb import Client
from src.infra.logger import setup_logging
from src import get_db_conn, get_vdb_client, get_embedd
from src.database import fetch_all_rows, insert_documents
from src.embeddings import BaseEmbeddings

# Initialize logger and settings
logger = setup_logging(name="ROUTE-CHUNKS-EMBEDDING")

embedding_route = APIRouter()


@embedding_route.post("/embedding", response_class=JSONResponse)
async def embedding(
    conn: Connection = Depends(get_db_conn),
    vdb_client: Client = Depends(get_vdb_client),
    embedding: BaseEmbeddings = Depends(get_embedd)
):
    """
    Embeds text chunks from the database using a specified embedding model.

    Args:
        request (Request): The FastAPI request object.
        embedd_name (str): Name of the embedding model to be used.

    Returns:
        JSONResponse: HTTP response indicating success or failure with appropriate status.
    """
    try:
        if not embedding:
            logger.error("Embedding model not initialized.")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Embedding service unavailable."
            )

        if not conn:
            logger.error("Database connection is None.")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database service unavailable."
            )

        if not vdb_client:
            logger.error("Vector DB client is None.")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Vector database service unavailable."
            )

        logger.debug("Fetching chunks from the database.")
        chunks = fetch_all_rows(conn=conn, table_name="chunks", columns=["text", "id"])
        if not chunks:
            logger.warning("No chunks found in the database.")
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail="No chunks found in the database."
            )

        logger.info("%d chunks fetched from the database.", len(chunks))

        success_count = 0
        for chunk in chunks:
            text, chunk_id = chunk["text"], chunk["id"]
            try:
                logger.debug("Embedding chunk ID %s", chunk_id)
                embedding_vector = embedding.embed_texts([text])[0]

                insert_documents(
                    client=vdb_client,
                    collection_name="chunks",
                    ids=[chunk_id],
                    embeddings=[embedding_vector],
                    documents=[text],
                    metadatas=None
                )

                logger.debug("Chunk ID %s embedded and inserted.", chunk_id)
                success_count += 1

            except Exception as embed_err:  # broad exception handling is fine here
                logger.error("Error embedding chunk ID %s: %s", chunk_id, embed_err)

        logger.info("Successfully embedded %d out of %d chunks.", success_count, len(chunks))
        return JSONResponse(
            content={"status": "success",
                     "message": f"{success_count} chunks embedded successfully."},
            status_code=HTTP_200_OK
        )

    except HTTPException as http_exc:
        logger.error("HTTPException: %s", http_exc.detail)
        raise http_exc

    except Exception as e:
        logger.error("Unexpected error in embedding endpoint")
        return JSONResponse(
            content={"status": "error", "detail": str(e)},
            status_code=HTTP_500_INTERNAL_SERVER_ERROR
        )
