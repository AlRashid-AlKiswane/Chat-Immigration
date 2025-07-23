"""
Live RAG (Retrieval-Augmented Generation) API Endpoint

This endpoint provides real-time question answering using a RAG pipeline that:
1. Generates embeddings for the input query
2. Retrieves relevant documents from the vector database
3. Generates a response using the LLM with retrieved context
"""

# pylint: disable=wrong-import-position
# Standard library imports
import logging
import os
import sys

# Special SQLite configuration
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
    logging.debug("Main directory path configured: %s", MAIN_DIR)
except (ImportError, OSError) as e:
    logging.critical("Failed to set up main directory path: %s", e, exc_info=True)
    sys.exit(1)

# Third-party imports
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR
)

from chromadb import Client

# Local application imports
from src.infra.logger import setup_logging
from src import get_vdb_client, get_embedd
from src.database import search_documents
from src.schema import RAGConfig
from src.embeddings import BaseEmbeddings

logger = setup_logging()

live_rag_route = APIRouter()

@live_rag_route.post("/live_rag", response_class=JSONResponse)
async def live_rag(
    query: str,
    rag_config: RAGConfig = Depends(),
    vdb_client: Client = Depends(get_vdb_client),
    embedding: BaseEmbeddings = Depends(get_embedd),
) -> JSONResponse:
    """Execute a live RAG pipeline for question answering."""

    logger.info(f"Starting RAG processing for query: '{query}'")

    # Validate input
    if not query.strip():
        logger.warning("Empty query received")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="query cannot be empty"
        )

    try:
        # Generate embeddings and retrieve documents
        logger.debug("Generating embeddings for query")
        query_embedding = embedding.embed_texts(texts=[query])[0]

        # Proper check for embedding validity
        if query_embedding is None or len(query_embedding) == 0:
            raise ValueError("Invalid embedding generated - empty or None")

        retrieved_docs = search_documents(
            client=vdb_client,
            collection_name="chunks",
            query_embedding=query_embedding,
            n_results=rag_config.n_results,
            include_metadata=rag_config.include_metadata
        )

        # Handle case where search_documents returns None
        if retrieved_docs is None:
            logger.warning("Document search returned None")
            retrieved_docs = []

        logger.info(f"Retrieved {len(retrieved_docs)} relevant documents")

        if not retrieved_docs:
            logger.warning("No relevant documents found")
            return JSONResponse(
                content={
                    "answer": "I couldn't find relevant information to answer your question.",
                    "sources": [],
                    "distances": [],
                    "metadata": {
                        "documents_retrieved": 0,
                        "warning": "No relevant documents found"
                    }
                },
                status_code=HTTP_200_OK
            )

        # Prepare response
        response_data = {
            "answer": retrieved_docs["docs"],
            "sources": retrieved_docs["scores"],
            "distances": retrieved_docs["distances"],
            "metadata": retrieved_docs["metas"]
        }

        logger.info("Successfully generated RAG response")
        return JSONResponse(content=response_data, status_code=HTTP_200_OK)

    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"RAG pipeline failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your question"
        ) from e
