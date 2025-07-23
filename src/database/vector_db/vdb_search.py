"""

"""
from typing import Any, Dict, List, Optional, Tuple
from chromadb import Client
from chromadb.errors import ChromaError
from src.infra.logger import setup_logging

logger = setup_logging(name="VECTORE-DB")

def search_documents(
    client: Client,
    query_embedding: List[float],
    collection_name: str = "Chunks",
    n_results: int = 5,
    include_metadata: bool = False
) -> Dict[str, Any]:
    """
    Search ChromaDB for similar documents using an embedding vector.
    """
    try:
        if hasattr(query_embedding, "tolist"):
            query_embedding = query_embedding.tolist()

        collection = client.get_collection(name=collection_name)

        query_result = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=[
                "documents", "distances", "metadatas"] 
                if include_metadata else ["documents", "distances"]
        )

        docs = query_result["documents"][0]
        scores = [1 - d for d in query_result["distances"][0]]
        metas = query_result.get("metadatas", [[None]])[0]

        return {
            "docs": docs,
            "scores": scores,
            "distances": query_result["distances"][0],
            "metas": metas
        }

    except ChromaError as e:
        logger.error("ChromaDB search error: %s", e)
        return None
    except Exception as e:
        logger.error("Unexpected error during search: %s", e)
        return None
