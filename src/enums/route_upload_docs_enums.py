"""
File Upload Log Messages

This module defines standardized log messages for file upload operations
using an Enum class. These messages ensure consistent logging across all
file upload components of the API.

The messages are categorized by operation type and include format placeholders
for dynamic values. Each message has an associated docstring explaining its
purpose and usage context.

Categories:
    - File Validation: Messages for file type/extension validation
    - File Operations: Messages for file saving and handling
    - Upload Handling: Messages for upload processing
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
