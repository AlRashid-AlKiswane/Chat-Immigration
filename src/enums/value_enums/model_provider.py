from enum import Enum

class ModelProvider(str, Enum):
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    COHERE = "cohere"
    GOOGLE = "google"
    LOCAL = "local"

