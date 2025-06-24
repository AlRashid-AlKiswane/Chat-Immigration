


from pydantic import BaseModel, Field, confloat, conint
from typing import Optional, List, Dict, Any

class RAGConfig(BaseModel):
    """
    Configuration model for Retrieval-Augmented Generation (RAG) systems.

    Attributes:
        score_threshold: Minimum similarity score for retrieved documents (0.0 to 1.0)
        n_results: Number of documents to retrieve (positive integer)
        include_metadata: Whether to include document metadata in results
        search_filters: Optional filters for document retrieval
        embedding_model: Name of the embedding model to use
        hybrid_search: Whether to use hybrid (dense + sparse) retrieval
        rerank: Whether to enable results reranking
        rerank_model: Model to use for reranking (if enabled)
        top_k_rerank: Number of results to rerank (if enabled)
    """
    n_results: int = Field(
        default=5,
        description="Number of documents to retrieve (must be positive)"
    )
    include_metadata: bool = Field(
        default=True,
        description="Include document metadata in retrieval results"
    )

