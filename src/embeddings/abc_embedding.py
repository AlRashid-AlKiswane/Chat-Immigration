"""
Text Embeddings Abstract Base Class Module

Defines the abstract interface for all text embedding implementations in the system.
Provides a consistent contract for embedding models regardless of the underlying
implementation (e.g., OpenAI, HuggingFace, Cohere, or custom models).

Key Components:
- BaseEmbeddings: ABC that enforces the required embedding interface
- Standardized input/output types for text embedding operations
- Batch processing capability declaration

Usage:
    Implement this interface to add new embedding providers:
    
    class MyEmbeddings(BaseEmbeddings):
        def embed_texts(self, texts, batch_size=None):
            # Implementation here
            return embeddings

Note:
    All concrete implementations must handle both single strings and lists of strings,
    and should document their specific batch processing capabilities.
"""

from abc import ABC, abstractmethod
from typing import List, Union, Optional


class BaseEmbeddings(ABC):
    """
    Abstract base class for text embedding models.

    This class defines the standard interface for all embedding implementations,
    ensuring consistent behavior across different embedding providers and models.

    Subclasses must implement the `embed_texts` method to provide concrete
    embedding functionality.
    """

    @abstractmethod
    def embed_texts(
        self,
        texts: Union[List[str], str],
        batch_size: Optional[int] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for the input text(s).

        Args:
            texts: Input text(s) to embed. Can be a single string or a list of strings.
            batch_size: Optional batch size for processing multiple texts efficiently.
                       Implementations may use this to optimize performance.

        Returns:
            List of embeddings, where each embedding is represented as a list of floats.
            For single string input, returns a list containing one embedding.
            For list input, returns embeddings in the same order as input texts.

        Raises:
            ValueError: If input texts are empty or invalid
            EmbeddingError: If embedding generation fails
            NotImplementedError: If batch processing is not supported by the implementation
        """
        # pylint: disable=unnecessary-pass
        pass
