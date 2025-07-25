"""
API Route Log Messages

This module defines standardized log messages for all API routes using Enum classes.
These messages ensure consistent logging across all application components.

Categories:
    - Validation: Input validation messages
    - Operations: Core operation logging
    - Status: Progress/state updates
    - Errors: Error conditions
    - System: Infrastructure-level issues

Design Principles:
    1. Placeholders ({}) for dynamic values
    2. Self-documenting with context in docstrings
    3. Categorized by operation phase
    4. Ready for i18n (all strings in one place)
    5. Type-safe via Enum
"""

from enum import Enum


class FileUploadMsg(Enum):
    """Standardized messages for file upload operations with format placeholders."""

    # --- File Validation Messages ---
    INVALID_FILE_TYPE = "Attempted upload with disallowed file type: {}"
    """Warning when an unsupported file type is detected."""

    # --- File Operations Messages ---
    FILE_SAVED = "File '{}' saved at '{}'"
    """Info message when a file is successfully saved."""

    FILE_SAVE_ERROR = "Failed to save uploaded file: {}"
    """Error when file saving operation fails."""

    # --- Upload Handling Messages ---
    SINGLE_UPLOAD_SUCCESS = "Single file '{}' uploaded successfully"
    """Info message for successful single file upload."""

    MULTI_UPLOAD_SUCCESS = "Batch upload processed - {} successful, {} failed"
    """Info message for batch upload completion."""

    # --- Error Handling Messages ---
    UPLOAD_ERROR = "Unexpected error during file upload: {}"
    """Error when an unexpected upload error occurs."""

    FILE_VALIDATION_ERROR = "File validation failed for '{}': {}"
    """Error when file validation fails."""

    # --- System Messages ---
    DIR_SETUP_ERROR = "Failed to set up upload directory: {}"
    """Error when upload directory cannot be created."""

    @staticmethod
    def get_http_detail(msg_enum, *args) -> str:
        """Helper to create consistent HTTP error details from enum messages."""
        return msg_enum.value.format(*args)


class DocsToChunks(Enum):
    """Standardized messages for document chunking API operations"""

    # --- Initialization ---
    API_STARTED = "[ROUTE(S)] [DOCSTOCHUNKS] Chunking API initialized"
    """API ready to process documents. Version: {version} | Endpoint: {endpoint}"""

    # --- Processing ---
    PROCESS_STARTED = "[ROUTE(S)] [DOCSTOCHUNKS] Starting chunking for: {}"
    """Document source: {source_type} | Reset flag: {do_reset}"""

    TABLE_CLEARED = "[ROUTE(S)] [DOCSTOCHUNKS] Cleared 'chunks' table"
    """Table: {table_name} | Rows affected: {row_count}"""

    NO_DOCUMENTS = "[ROUTE(S)] [DOCSTOCHUNKS] No valid documents found"
    """File path: {file_path} | File exists: {file_exists}"""

    CHUNKS_CREATED = "[ROUTE(S)] [DOCSTOCHUNKS] Created {} chunks"
    """Avg chunk size: {avg_tokens} tokens | Documents: {doc_count}"""

    # --- Database Operations ---
    CHUNKS_INSERTED = "[ROUTE(S)] [DOCSTOCHUNKS] Inserted {} chunks"
    """Table: {table_name} | Duration: {duration_ms:.1f}ms"""

    # --- Error Handling ---
    VALIDATION_ERROR = "[ROUTE(S)] [DOCSTOCHUNKS] {}"
    """Field: {field} | Value: {value} | Rule: {validation_rule}"""

    DB_ERROR = "[ROUTE(S)] [DOCSTOCHUNKS] Operation failed: {}"
    """Table: {table_name} | Query: {query} | Error code: {error_code}"""

    UNEXPECTED_ERROR = "[ROUTE(S)] [DOCSTOCHUNKS] Unexpected error: {}"
    """Trace ID: {trace_id} | Component: {component}"""

    # --- Success ---
    OPERATION_SUCCESS = "[ROUTE(S)] [DOCSTOCHUNKS] Successfully processed request"
    """Chunks: {chunk_count} | Documents: {doc_count} | Duration: {total_seconds:.1f}s"""
