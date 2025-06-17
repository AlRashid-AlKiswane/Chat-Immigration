"""
Document Processing Log Messages

This module defines standardized log messages for document processing operations
using an Enum class. These messages ensure consistent logging across all document
loading and chunking components of the application.

The messages are categorized by operation type and include format placeholders
for dynamic values. Each message has an associated docstring explaining its
purpose and usage context.

Categories:
    - File Handling: Messages for file system operations
    - Document Loading: Messages for document parsing
    - Chunk Processing: Messages for text splitting operations
    - Metadata Handling: Messages about document metadata
    - Error Handling: Messages for error conditions
    - System: Messages for system-level issues

Design Principles:
    1. Consistent formatting with clear placeholder positions
    2. Self-documenting message purposes
    3. Categorized by operation type
    4. Ready for internationalization (i18n)
    5. Type-safe through Enum implementation
"""

from enum import Enum


class DocToChunksMsg(Enum):
    """
    Standardized messages for converting documents to chunks with parameter placeholders.
    Uses %s style placeholders for lazy evaluation.
    """

    # --- File Handling Messages ---
    DIRECTORY_ERROR = "Failed to list files in directory: %s"
    """Error when unable to scan document directory."""

    NO_FILES_WARNING = "No valid files found to process"
    """Warning when no processable files are found."""

    UNSUPPORTED_TYPE = "Unsupported file type: %s"
    """Debug message for skipped file types."""

    UNEXPECTED_LISTING_ERROR = "Unexpected error listing files: %s"
    """Critical error when an unknown exception occurs during file listing."""

    # --- Document Loading Messages ---
    PDF_LOAD_SUCCESS = "Loaded PDF file: %s"
    """Debug message for successful PDF loading."""

    PDF_LOAD_FAILURE = "Failed to load PDF with PyMuPDF: %s"
    """Warning when PDF loading fails."""

    FALLBACK_TEXT_LOAD = "Fallback to text loader: %s"
    """Info message about fallback loading attempt."""

    TEXT_LOAD_FAILURE = "Failed to load file with TextLoader: %s"
    """Error when text loading fails."""

    # --- Chunk Processing Messages ---
    CHUNKING_SUCCESS = "Processed %d chunks from %s"
    """Info message for successful chunking."""

    NO_CHUNKS_WARNING = "No chunks were generated from the documents"
    """Warning when chunking produces no output."""

    # --- Metadata Handling Messages ---
    METADATA_EXTRACTION_ERROR = "Failed to extract metadata: %s"
    """Error when metadata extraction fails."""

    # --- Error Handling Messages ---
    PROCESSING_ERROR = "Error processing file %s: %s"
    """Error during file processing."""

    UNEXPECTED_ERROR = "Unexpected error processing file %s: %s"
    """Critical error during processing."""

    OUTPUT_ERROR = "Failed to construct output dictionary: %s"
    """Error when preparing final output."""

    # --- System Messages ---
    CONFIG_ERROR = "Configuration error: %s"
    """Error in processing configuration."""

    def __str__(self):
        """Returns the raw message string with placeholders"""
        return self.value

    def format(self, *args):
        """Formats the message with the given arguments"""
        return self.value % args
