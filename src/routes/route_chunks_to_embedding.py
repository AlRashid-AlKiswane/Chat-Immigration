"""
Embedding Route Module

This module provides an API endpoint for generating vector embeddings
 from text chunks stored in a SQLite database.
The embedding is performed using the OpenAIEmbeddingModel.
 It ensures proper logging, error handling, and response formatting.
"""

import logging
import os
import sys
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
from sqlite3 import Connection  # Ensure Pylint recognizes it as a valid type
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from chromadb import Client

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs.logger import setup_logging
from src.helpers import get_db_conn, get_vdb_client
from src.database import fetch_all_rows, insert_documents
from src.embeddings import OpenAIEmbeddingModel, HuggingFaceModel

# Initialize logger and settings
logger = setup_logging()

embedding_route = APIRouter()


@embedding_route.post("/embedding", response_class=JSONResponse)
async def embedding(
    request: Request,
    embedd_name: str,
    conn: Connection = Depends(get_db_conn),
    vdb_client: Client = Depends(get_vdb_client)
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
        model_name = embedd_name
        logger.debug("Attempting to initialize embedding model: %s", model_name)

        embedding_model = None
        if model_name.upper() == "OPENAI":
            embedding_model = OpenAIEmbeddingModel()
            logger.info("Successfully initialized OpenAI embedding model")

        elif model_name.upper() == "LOCAL":
            embedding_model = HuggingFaceModel()
            logger.info("Successfully initialized local HuggingFace embedding model")

        else:
            error_msg = f"Invalid model name: {model_name}. Valid options are 'OPENAI' or 'LOCAL'"
            logger.error(error_msg)
            raise ValueError(error_msg)

        request.app.state.embedd_name = model_name
        request.app.state.embedding = embedding_model

        logger.info("[Model] Embedding model '%s' loaded successfully.", model_name)
        logger.info("Embedding request received with model name: %s", embedd_name)

        if not embedding_model:
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
                embedd_vector = embedding_model.embed_texts(texts=[text])

                insert_documents(
                    client=vdb_client,
                    collection_name="Chunks",
                    ids=chunk_id,
                    embeddings=embedd_vector,
                    documents=text,
                    metadatas=None
                )
                logger.debug("Chunk ID %s embedded and inserted successfully.", chunk_id)
                success_count += 1

            except Exception as embed_err:
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