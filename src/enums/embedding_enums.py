"""
Embedding Generation Log Messages

This module defines standardized log messages for embedding operations using Enum classes.
These messages ensure consistent logging across all embedding-related components.

Categories:
    - Initialization: Model setup and configuration
    - Validation: Input validation messages
    - Processing: Core embedding generation
    - Batch Handling: Batch processing operations
    - Errors: Error conditions
    - System: Infrastructure-level issues

"""



from enum import Enum

class OPenAPIEmbeddingMsg(Enum):
    """Standardized messages for OpenAI embedding operations with lazy formatting."""

    # --- Initialization ---
    MODEL_INIT_START = "[EMBEDDING] [api_model] Initializing OpenAI embedding model"
    """Info: Embedding model initialization started."""

    MODEL_INIT_COMPLETE = "[EMBEDDING] [api_model] Model initialized: %s (max batch: %d)"
    """Info: Successful model initialization with config."""

    # --- Validation ---
    INVALID_API_KEY = "[EMBEDDING] [api_model] Missing or invalid OpenAI API key"
    """Error: API key validation failed."""

    INVALID_MODEL_NAME = "[EMBEDDING] [api_model] Invalid model name: %s"
    """Error: Model name validation failed."""

    EMPTY_INPUT = "[EMBEDDING] [api_model] Received empty input texts"
    """Warning: No texts provided for embedding."""

    # --- Processing ---
    START_EMBEDDING = "[EMBEDDING] [api_model] Generating embeddings for %d text(s)"
    """Info: Started embedding generation."""

    PROCESSING_TEXT = "[EMBEDDING] [api_model] Processing text (%d chars)"
    """Debug: Processing individual text."""

    # --- Batch Operations ---
    BATCH_START = "[EMBEDDING] [api_model] Processing batch %d/%d of %d texts"
    """Debug: Started processing a batch."""

    BATCH_SUCCESS = "[EMBEDDING] [api_model] Batch %d completed successfully"
    """Info: Batch processed successfully."""

    OPENAI_BATCH_ERROR = "[EMBEDDING] [api_model] OpenAI API error for batch %d-%d: %s"

    # --- Errors ---
    API_ERROR = "[EMBEDDING] [api_model] OpenAI API error: %s"
    """Error: API request failed."""


    UNEXPECTED_ERROR = "[EMBEDDING] [api_model] Unexpected error processing batch %d-%d: %s"
    """Error: Unexpected failure occurred."""

    # Success Messages
    GENERATION_SUCCESS = "Successfully generated embeddings for %d texts across %d batches"
    """Logged when embeddings are successfully generated"""
    
    # Error Messages
    GENERATION_FAILED = "Failed to generate embeddings: %s"
    """Logged when embedding generation fails"""




class HuggingFaceMsg(Enum):
    """Enum containing message templates for HuggingFaceModel."""
    # Initialization Messages
    MODEL_INIT_SUCCESS = "[Embedding] [local_model] Embedding model '%s' initialized."
    """Logged when model successfully initializes. %s = model name"""
    
    MODEL_INIT_FAILED = "[Embedding] [local_model] Failed to load embedding model '%s': %s"
    """Logged when model fails to initialize. %s = model name, error"""

    # Input Validation
    EMPTY_INPUT_ERROR = "[Embedding] [local_model] Input texts cannot be empty."
    """Error raised when empty input is provided for embedding"""

    # Embedding Process
    EMBEDDING_SUCCESS = "[Embedding] [local_model] Generated embedding for text: '%.30s...'"
    """Logged after successfully generating embedding. %.30s = text sample"""
    
    EMBEDDING_FAILURE = "[Embedding] [local_model] Error generating embedding: %s"
    """Logged when embedding generation fails. %s = error details"""

    # Model Information
    MODEL_INFO_RETRIEVED = "[Embedding] [local_model] Retrieved model information for '%s'"
    """Logged when fetching model metadata. %s = model info"""
