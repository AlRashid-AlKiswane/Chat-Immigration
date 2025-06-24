"""
LLM Generation Route Module

Handles RAG (Retrieval-Augmented Generation) requests with:
- Document retrieval from vector DB
- LLM response generation
- Query caching
- Comprehensive error handling
"""

# Standard library imports
import logging
import os
import sys
from typing import Optional

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

# pylint: disable=wrong-import-position
# Third-party imports
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR
)

from chromadb import Client
from sqlite3 import Connection

# Local application imports
from src.logs.logger import setup_logging
from src.helpers import get_db_conn, get_vdb_client, get_embedd, get_llm
from src.database import fetch_all_rows, insert_query_response, search_documents
from src.schema import GenerationParameters, RAGConfig
from src.embeddings import BaseEmbeddings
from src.llms import BaseLLM


# Initialize logger
logger = setup_logging()
llm_generation_route = APIRouter()

@llm_generation_route.post("/generation", response_class=JSONResponse)
async def generation(
    generation_parameters: GenerationParameters,
    rag_config: RAGConfig,
    user_id: Optional[str] = None,
    prompt: Optional[str] = None,
    conn: Connection = Depends(get_db_conn),
    vdb_client: Client = Depends(get_vdb_client),
    embedding: BaseEmbeddings = Depends(get_embedd),
    llm: BaseLLM = Depends(get_llm)
) -> JSONResponse:
    """
    Handle RAG generation request with caching and retrieval.

    Args:
        request: FastAPI Request object
        generation_parameters: Parameters for LLM generation
        rag_config: RAG configuration
        user_id: Optional user identifier for caching
        prompt: Input prompt text
        conn: Database connection
        vdb_client: Vector database client
        embedding: Embedding model
        llm: Language model

    Returns:
        JSONResponse: Generated response or cached result

    Raises:
        HTTPException: For various error scenarios
    """
    try:
        # Validate required parameters
        if not all([prompt, user_id, generation_parameters]):
            logger.error("Missing required parameters")
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Missing required parameters: prompt, user_id or generation_parameters"
            )

        logger.debug(f"Starting generation for user {user_id} with prompt: {prompt[:50]}...")

        # Check cache
        try:
            cache_result = fetch_all_rows(
                conn=conn,
                table_name="query_response",
                columns=["user_id", "response", "query"],
                cache_key=[user_id, prompt],
                where_clause=f"user_id = '{user_id}' AND query = '{prompt}'"
            )

            if cache_result and prompt == cache_result[0]["query"]:
                logger.debug("Returning cached response")
                return JSONResponse(
                    status_code=HTTP_200_OK,
                    content={
                        "response": cache_result[0]["response"],
                        "source": "cache",
                        "user_id": user_id
                    }
                )
        except Exception as e:
            logger.error(f"Cache lookup failed: {str(e)}", exc_info=True)
            # Continue with generation even if cache fails

        # Generate embeddings and retrieve documents
        try:
            logger.debug("Generating embeddings for query")
            query_embedding = embedding.embed_texts(texts=prompt)

            retrieved_docs = search_documents(
                client=vdb_client,
                collection_name="Chunks",
                query_embedding=query_embedding,
                n_results=rag_config.n_results,
                include_metadata=rag_config.include_metadata
            )
            logger.debug(f"Retrieved {len(retrieved_docs)} documents")
        except Exception as e:
            logger.error(f"Document retrieval failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Document retrieval failed"
            ) from e

        # Generate response
        try:
            prompt_template = f"{prompt}\n\nContext:\n{retrieved_docs}"
            logger.debug("Generating LLM response")

            response = llm.generate_response(
                prompt=prompt_template,
                **generation_parameters.dict()
            )

            # Cache the response
            try:
                insert_query_response(
                    conn=conn,
                    user_id=user_id,
                    query=prompt,
                    response=response
                )
            except Exception as e:
                logger.warning(f"Failed to cache response: {str(e)}")

            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "response": response,
                    "source": "generation",
                    "user_id": user_id,
                    "retrieved_docs_count": len(retrieved_docs)
                }
            )

        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Response generation failed"
            ) from e

    except HTTPException:
        raise
    except Exception as e:
        logger.critical(f"Unexpected error in generation endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from e
