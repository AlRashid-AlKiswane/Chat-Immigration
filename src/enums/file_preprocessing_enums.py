"""
File Preprocessing Log Messages

This module defines standardized log messages for file preprocessing operations
using an Enum class. These messages ensure consistent logging across all file
handling components of the application.

The messages are categorized by operation type and include format placeholders
for dynamic values. Each message has an associated docstring explaining its
purpose and usage context.

Categories:
    - Input Validation: Messages for invalid file inputs
    - File Type Handling: Messages for unsupported file types
    - Extension Handling: Messages related to file extensions
    - Name Handling: Messages for filename processing
    - Sanitization: Messages for filename cleaning operations
    - Generation: Messages for new filename creation
    - Error Handling: Messages for error conditions
    - System: Messages for filesystem-related issues


Design Principles:
    1. Consistent formatting with clear placeholder positions
    2. Self-documenting message purposes
    3. Categorized by operation type
    4. Ready for internationalization (i18n)
    5. Type-safe through Enum implementation
"""

from enum import Enum


class FilePreprocessingMsg(Enum):
    """Standardized messages for file preprocessing with format placeholders."""

    # Input validation
    INVALID_INPUT = "Invalid filename provided: {}"
    """Error message when input filename is invalid (empty or wrong type)"""

    # File type handling
    UNSUPPORTED_TYPE = "File type not in allowed types: {}"
    """Warning when file extension isn't in allowed types"""

    # Extension handling
    MISSING_EXTENSION = "Missing file extension in: {}, using default"
    """Warning when file has no extension"""
    DEFAULT_EXTENSION_USED = "Using default extension for: {}"
    """Info message when default extension is applied"""

    # Name handling
    EMPTY_NAME = "Empty filename provided, using default"
    """Warning when filename stem is empty"""

    # Sanitization
    NAME_SANITIZED = "Sanitized filename from {} to {}"
    """Debug message showing name before/after sanitization"""

    # Generation
    FILENAME_GENERATED = "Generated new filename: {} from original: {}"
    """Debug message showing final generated filename"""

    # Error handling
    VALIDATION_ERROR = "Validation error in filename generation: {}"
    """Error message for validation failures"""
    GENERATION_ERROR = "Unexpected error generating filename: {}"
    """Error message for unexpected generation failures"""
    FALLBACK_USED = "Using fallback filename: {}"
    """Warning message when fallback filename is generated"""

    # System
    PATH_ERROR = "Filesystem path error: {}"
    """Error message for path-related issues"""
