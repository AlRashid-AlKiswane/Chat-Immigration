
from enum import Enum

class SentenceEmbeddingLogMessages(Enum):
    # Initialization messages
    INIT_SUCCESS = "Embedding model '%s' initialized."
    INIT_FAILURE = "Failed to load embedding model '%s': %s"

    # Embedding process
    EMPTY_INPUT = "Empty text provided for embedding."
    GENERATION_SUCCESS = "Generated embedding for text: '%.30s...'"
    GENERATION_FAILURE = "Error generating embedding: %s"
