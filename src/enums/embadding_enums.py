"""
"""



from enum import Enum

class EmbeddingLogMessages(Enum):
    """ """
    # Initialization messages
    INIT_SUCCESS = "OpenAIEmbeddingModel initialized with model: %s"
    MISSING_API_KEY = "OpenAI API key is missing."
    MISSING_MODEL_NAME = "OpenAI embedding model name is missing."

    # Embedding input validation
    EMPTY_INPUT = "No texts provided for embedding."

    # Batch processing
    PROCESSING_BATCH = "Processing batch %d-%d of %d texts"
    BATCH_API_ERROR = "OpenAI API error for batch %d-%d: %s"
    BATCH_UNEXPECTED_ERROR = "Unexpected error processing batch %d-%d: %s"

    # Embedding completion
    SUCCESSFUL_EMBEDDING = (
        "Successfully generated embeddings for %d texts across %d batches"
    )

    # Final failure
    FINAL_FAILURE = "Failed to generate embeddings: %s"

# Example usage in your existing code:
# logger.info(EmbeddingLogMessages.INIT_SUCCESS.value, self.model_name)

class SentenceEmbeddingLogMessages(Enum):
    # Initialization messages
    INIT_SUCCESS = "Embedding model '%s' initialized."
    INIT_FAILURE = "Failed to load embedding model '%s': %s"

    # Embedding process
    EMPTY_INPUT = "Empty text provided for embedding."
    GENERATION_SUCCESS = "Generated embedding for text: '%.30s...'"
    GENERATION_FAILURE = "Error generating embedding: %s"
