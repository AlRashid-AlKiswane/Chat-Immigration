"""

"""
from typing import Any, Dict, List, Optional, Tuple
from chromadb import Client
from chromadb.errors import ChromaError


from src.infra import setup_logging

logger = setup_logging(name="VECTORE-DB-SEARCH")

def search_documents(
    client: Client,
    query_embedding: List[float],
    collection_name: str = "Chunks",
    n_results: int = 5,
    include_metadata: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Search ChromaDB for similar documents using an embedding vector.

    Args:
        client (Client): ChromaDB client instance.
        query_embedding (List[float]): A single embedding vector (1D list or numpy array).
        collection_name (str): Name of the collection to query.
        n_results (int): Number of top results to return.
        include_metadata (bool): Whether to include metadata in the result.

    Returns:
        Optional[Dict[str, Any]]: Dictionary with keys "docs", "scores", "distances", and optionally "metas";
                                  or None if no results or error occurs.
    """
    logger.info("● Starting document search in collection '%s'", collection_name)

    try:
        # Step 1: Normalize embedding input
        logger.debug("● Checking and converting query_embedding to list format if needed...")
        if hasattr(query_embedding, "tolist"):
            query_embedding = query_embedding.tolist()
            logger.debug("● query_embedding converted using tolist().")

        if not query_embedding:
            logger.warning("● query_embedding is empty. Aborting search.")
            return None

        if isinstance(query_embedding[0], (float, int)):
            query_embeddings = [query_embedding]  # Wrap single vector in list
            logger.debug("● query_embedding is 1D. Wrapped to 2D list.")
        else:
            query_embeddings = query_embedding  # Already 2D
            logger.debug("● query_embedding is already 2D.")

        # Step 2: Get collection
        logger.info("● Retrieving collection '%s' from ChromaDB...", collection_name)
        collection = client.get_collection(name=collection_name)

        # Step 3: Query the collection
        logger.info("● Executing vector search for top %d results...", n_results)
        include_fields = ["documents", "distances", "metadatas"] if include_metadata else ["documents", "distances"]
        query_result = collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results,
            include=include_fields
        )
        logger.debug("● Raw query result: %s", query_result)

        # Step 4: Extract and validate results
        documents = query_result.get("documents", [])
        distances = query_result.get("distances", [])
        metadatas = query_result.get("metadatas", [[None]])

        if not documents or not distances or not documents[0] or not distances[0]:
            logger.warning("● Empty query result: no documents or distances returned.")
            return None

        docs = documents[0]
        scores = [1 - d for d in distances[0]]  # Similarity = 1 - distance
        metas = metadatas[0] if include_metadata else [None] * len(docs)

        logger.info("● Search completed successfully with %d result(s).", len(docs))
        logger.debug("● Top document: %s", docs[0] if docs else "None")
        logger.debug("● Scores: %s", scores)
        logger.debug("● Distances: %s", distances[0])
        logger.debug("● Metadatas: %s", metas)

        return {
            "docs": docs,
            "scores": scores,
            "distances": distances[0],
            "metas": metas
        }

    except ChromaError as e:
        logger.error("● ChromaDB search error: %s", e)
        return None
    except Exception as e:
        logger.error("● Unexpected error during search: %s", e, exc_info=True)
        return None
