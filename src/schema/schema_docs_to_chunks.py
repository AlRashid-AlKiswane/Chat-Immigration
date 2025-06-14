"""
Document Chunking Data Model

This module defines the Pydantic model for representing chunked document data with metadata.
The ChunkData model provides a structured way to store and validate:
- Text content chunks
- Associated page numbers
- Source document references
- Author information

The model ensures data consistency when processing documents through chunking pipelines,
making it suitable for document processing, RAG (Retrieval-Augmented Generation) systems,
and knowledge management applications.

Example:
    >>> chunk_data = ChunkData(
    ...     chunks=["First paragraph", "Second paragraph"],
    ...     pages=[1, 2],
    ...     sources=["doc.pdf", "doc.pdf"],
    ...     authors=["John Doe", "John Doe"]
    ... )
    >>> print(chunk_data.chunks[0])
    'First paragraph'

Key Features:
    - Type validation for all fields
    - Parallel lists ensure consistent metadata alignment
    - Pydantic BaseModel integration for serialization/deserialization
    - Clear field descriptions for API documentation
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChunkData(BaseModel):
    """Structured representation of chunked document content with metadata.

    Attributes:
        chunks: List of extracted text segments.
            Each string represents one logical chunk of content.
        pages: Page numbers corresponding to each chunk.
            Must be same length as chunks list.
        sources: Source document identifiers for each chunk.
            Typically file paths or document IDs.
        authors: Authors/contributors associated with each chunk.
            Useful for multi-author documents.

    Raises:
        ValidationError: If lists have mismatched lengths or invalid types.
    """

    chunks: List[str] = Field(..., description="List of text chunks from the document")
    pages: List[int] = Field(..., description="List of page numbers for each chunk")
    sources: List[str] = Field(
        ..., description="List of source file paths or names for each chunk"
    )
    authors: List[str] = Field(..., description="List of authors for each chunk")


class ChunksRequest(BaseModel):
    """Request model for document chunking operation.

    Attributes:
        file_path: Optional path to a specific file to process. If not provided,
                  all valid files in the configured directory will be processed.
        do_rest: Flag indicating whether to reset/clear existing chunks before processing.
                 0 = no reset, 1 = reset existing chunks.
    """

    file_path: Optional[str] = Field(
        None,
        description="Optional specific file path to process. Leave empty to process all files in directory.",
    )
    do_rest: int = Field(
        0, description="Reset flag (0=no reset, 1=reset existing chunks)", ge=0, le=1
    )
