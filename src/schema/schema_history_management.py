
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, Dict, List, Any


from src.enums.value_enums import ModelProvider
from src.schema import ModelInfo


class ChatMessage(BaseModel):
    """Pydantic model for strongly-typed message storage"""
    content: str
    role: Literal["user", "ai"] = Field(..., description="Sender role")
    timestamp: float = Field(
        default_factory=lambda: datetime.now().timestamp())
    model_info: Optional["ModelInfo"] = Field(
        None,
        description="Required for AI messages, None for user messages"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProviderChatHistory(BaseModel):
    """Stores converstion history per provider"""
    user_id: str
    provider: ModelProvider
    messages: List[ChatMessage] = Field(default_factory=list)

    def add_message(self, message: ChatMessage):
        if message.role == "ai" and not message.model_info:
            raise ValueError("AI messages require model_info")
        self.messages.append(message)  # pylint: disable=no-member


# Usage Example:
history = ProviderChatHistory(
    user_id="user123",
    provider=ModelProvider.OPENAI.value,
    messages=[
        ChatMessage(
            content="Hello AI!",
            role="user"
        ),
        ChatMessage(
            content="Hi there!",
            role="ai",
            model_info=ModelInfo(
                name="gpt-4",
                provider=ModelProvider.OPENAI
            )
        )
    ]
)
