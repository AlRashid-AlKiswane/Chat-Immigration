"""
ChromaDB Search Operations Module.

This module provides functionality for performing similarity searches in ChromaDB collections
using query embeddings. It includes robust error handling, logging, and result filtering.
"""

import os
import sys
from typing import List, Optional, Tuple
import logging
from chromadb import Client
from chromadb.errors import ChromaError

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)


from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()

def search_documents(
    client: Client,
    collection_name: str,
    query_embedding: List[float],
    score_threshold: float = 0.5,
    n_results: int = 5,
    include_metadata: bool = False
) -> Optional[List[Tuple[str, float, Optional[dict]]]]:
    """
    Perform a similarity search in a ChromaDB collection using a query embedding.

    Args:
        client: Initialized ChromaDB client instance.
        collection_name: Name of the collection to search.
        query_embedding: Embedding vector for the search query.
        score_threshold: Minimum similarity score (0.0-1.0) for results (default: 0.5).
        n_results: Maximum number of results to return (default: 5).
        include_metadata: Whether to include document metadata in results (default: False).

    Returns:
        List of tuples containing (document_text, similarity_score, metadata) for each result,
        or None if the search failed. Metadata is None if include_metadata=False.

    Raises:
        ValueError: If input parameters are invalid.
        ChromaError: For ChromaDB-specific errors.
    """
    # Input validation
    if query_embedding is None:
        logger.error("Query embedding is None")
        raise ValueError("Query embedding cannot be None")

    if hasattr(query_embedding, "__len__") and len(query_embedding) == 0:
        logger.error("Query embedding is empty")
        raise ValueError("Query embedding cannot be empty")


    if not 0 <= score_threshold <= 1:
        logger.error("Invalid score threshold: %f", score_threshold)
        raise ValueError("Score threshold must be between 0.0 and 1.0")

    if n_results <= 0:
        logger.error("Invalid n_results: %d", n_results)
        raise ValueError("Number of results must be positive")

    try:
        logger.info(
            "Searching collection '%s' with threshold %.2f for %d results",
            collection_name, score_threshold, n_results
        )

        collection = client.get_collection(name=collection_name)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, 100),  # Limit to reasonable maximum
            include=[
                "documents", "distances", "metadatas"] 
                if include_metadata else ["documents", "distances"]
        )

        # Process results
        documents = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results.get(
            "metadatas",
            [None] * len(documents))[0] if include_metadata else [None] * len(documents)

        filtered_results = [
            (doc, 1 - dist, meta)  # Convert distance to similarity score
            for doc, dist, meta in zip(documents, distances, metadatas)
            if (1 - dist) >= score_threshold
        ]

        logger.debug(
            "Found %d results after filtering (from %d raw results)",
            len(filtered_results), len(documents)
        )

        return filtered_results[:n_results]  # Ensure we don't exceed requested count

    except ChromaError as ce:
        logger.error("ChromaDB search failed: %s", str(ce))
        raise
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Unexpected error during search: %s", str(e))
        return None
