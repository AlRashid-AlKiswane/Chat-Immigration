"""
history_management.py

Module for managing user chat histories in AI-powered applications.

This module provides an asynchronous, type-safe chat history manager
(`ChatHistoryManager`) that handles multi-user chat logs using:
- Custom Pydantic schemas (`ChatMessage`, `ProviderChatHistory`, `ModelInfo`)
- LangChain’s `ConversationBufferMemory` for in-memory chat management
- Dual storage: structured memory and LangChain memory
- Caching with LRU for performance

Features:
- Add validated user/AI messages to per-user history
- Store and retrieve chat history with support for time-based filtering
- Track active users and model provider usage statistics
- Clear chat history safely with logging and error handling

Dependencies:
- LangChain (conversation memory)
- Pydantic v2+ (data validation and serialization)
- Python built-ins: asyncio, datetime, logging, functools, etc.

Example usage:
>>> manager = ChatHistoryManager()
>>> await manager.add_message("user1", "Hello", "user", provider=ModelProvider.OPENAI)
>>> history = await manager.get_history("user1")
>>> print(history)

Author: Rama Amairy
Date: 2025-07-02
"""

import asyncio
import os
import sys
import logging
from datetime import datetime
from functools import lru_cache
from typing import Literal, Optional, List, Dict, Awaitable, Any
from pydantic import ValidationError


from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage


# Set up main directory path
try:
    MAIN_DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
# pylint: disable=logging-format-interpolation

from src.logs.logger import setup_logging
from src.schema import ChatMessage, ProviderChatHistory, ModelInfo
from src.enums.value_enums import ModelProvider

logger = setup_logging()


class ChatHistoryManager:
    """
    Enhanced chat history manager that works with your ProviderChatHistory schema.
    Features:
    - Async operations
    - LRU memory caching
    - Type-safe message handling
    - Dual storage (LangChain + ProviderChatHistory)
    """

    def __init__(self, max_cached_users: int = 1000):
        """
        Args:
        max_cached_users: Maximum users to keep in LRU cache
        """
        self.max_cached_users = max_cached_users
        self._history_store: Dict[str, ProviderChatHistory] = {}
        logger.info(
            f"ChatHistoryManager initialized with cache size: {max_cached_users}")

    @lru_cache(maxsize=1000)
    def _get_memory_sync(self, user_id: str) -> ConversationBufferMemory:
        """Sync method with LRU caching"""
        logger.debug(
            f"Creating ConversationBufferMemory for user_id={user_id}")
        return ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )

    async def get_memory(self, user_id: str) -> Awaitable[ConversationBufferMemory]:
        """Async wrapper for memory access"""
        logger.debug(f"Fetching memory asynchronously for user_id={user_id}")
        return await asyncio.to_thread(self._get_memory_sync, user_id)

    async def initialize_history(
        self,
        user_id: str,
        provider: ModelProvider
    ) -> ProviderChatHistory:
        """Initialize a new provider-specific history"""
        if user_id not in self._history_store:
            logger.info(
                f"Initializing history for user_id={user_id}, provider={provider}")
            self._history_store[user_id] = ProviderChatHistory(
                user_id=user_id,
                provider=provider,
                messages=[]
            )
        else:
            logger.debug(f"History already exists for user_id={user_id}")
        return self._history_store[user_id]

    async def add_message(
        self, user_id: str, content: str, role: Literal["user", "ai"],
        provider: ModelProvider,
        model_info: Optional[ModelInfo] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """
        Add a message with validation and dual storage

        Args:
            user_id: Unique user identifier
            content: Message content
            role: 'user' or 'ai'
            provider: Model provider enum
            model_info: Required for AI messages
            metadata: Additional message metadata

        Returns:
            The created ChatMessage instance
        """
        logger.debug(f"Adding message for user_id={user_id}, role={role}")
        
        try:
            # create validated message
            message = ChatMessage(
                content=content,
                role=role,
                model_info=model_info,
                metadata=metadata or {}
            )

            history = await self.initialize_history(user_id=user_id, provider=provider)

            # Add to structured storage
            history.add_message(message)

            # Add to LangChain memory (async)
            memory = await self.get_memory(user_id)
            msg_class = HumanMessage if role == "user" else AIMessage
            memory.chat_memory.add_message(msg_class(content=content))

            logger.info(f"Message added for {user_id} ({role})")
            return message

        except ValidationError as e:  # pylint: disable=undefined-variable
            logger.error(f"Validation failed: {e}", exc_info=True)
            raise ValueError(f"Invalid message: {e}") from e
        except Exception as e:
            logger.error(f"Storage failed: {e}", exc_info=True)
            raise RuntimeError(f"Message addition failed: {e}") from e

    async def get_history(
        self,
        user_id: str,
        limit: Optional[int] = None,
        since: Optional[datetime] = None
    ) -> ProviderChatHistory:
        """
        Retrieve complete conversation history with filters

        Args:
            user_id: Target user ID
            limit: Max messages to return
            since: Return messages after this timestamp

        Returns:
            ProviderChatHistory instance with filtered messages
        """
        logger.debug(
            f"Getting history for user_id={user_id}, limit={limit}, since={since}")
        logger.debug(f"DEBUG - Current storage: {self._history_store}")
        if user_id not in self._history_store:
            return ProviderChatHistory(
                user_id=user_id,
                provider=ModelProvider.OPENAI,  # Default
                messages=[]
            )
        history = self._history_store[user_id]

        # apply filters on date
        filtered_messages = history.messages.copy()
        if since:
            filtered_messages = [
                m for m in filtered_messages if datetime.fromtimestamp(m.timestamp) > since]
            logger.debug(
                f"Filtered messages since {since}: {len(filtered_messages)}")
        if limit is not None:
            filtered_messages = filtered_messages[-limit:]
            logger.debug(
                f"Applied limit {limit}: {len(filtered_messages)} messages")
        logger.info(
            f"Returning history with {len(filtered_messages)} messages for user {user_id}")
        return ProviderChatHistory(
            user_id=user_id,
            provider=history.provider,
            messages=filtered_messages
        )

    async def clear_history(self, user_id: str) -> None:
        """Clear all history for a user"""
        logger.info(f"Clearing history for user_id={user_id}")
        try:
            # Clear LangChain memory
            memory = await self.get_memory(user_id)
            memory.chat_memory.clear()

            # Clear structured storage
            self._history_store.pop(user_id, None)

            # Clear from LRU cache
            self._get_memory_sync.cache_clear()

            logger.info(f"Cleared history for {user_id}")

        except Exception as e:
            logger.error(f"Clear failed: {e}", exc_info=True)
            raise RuntimeError(f"History clearance failed: {e}") from e

    def get_active_users(self) -> List[str]:
        """List all users with stored history"""
        active_users = list(self._history_store.keys())
        logger.info(f"Active users retrieved: {active_users}")
        return active_users

    async def get_provider_usage(self) -> Dict[ModelProvider, int]:
        """Get message count per provider"""
        logger.debug("Calculating provider usage stats")
        stats = {}
        for history in self._history_store.values():
            stats[history.provider] = stats.get(
                history.provider, 0) + len(history.messages)
        logger.info(f"Provider usage stats: {stats}")
        return stats


# Example Usage
async def demo():
    """test function"""
    manager = ChatHistoryManager()

    # Add messages
    await manager.add_message(
        "user1",
        "What's the weather?",
        "user",
        provider=ModelProvider.OPENAI
    )

    await manager.add_message(
        "user1",
        "It's sunny and 72°F",
        "ai",
        provider=ModelProvider.OPENAI,
        model_info=ModelInfo(
            name="gpt-4",
            provider=ModelProvider.OPENAI
        ),
        metadata={"confidence": 0.95}
    )

    # Retrieve history
    history = await manager.get_history("user1")
    print(f"History for user1: {history.model_dump_json(indent=2)}")

    # Get provider stats
    stats = await manager.get_provider_usage()
    print(f"Provider stats: {stats}")

    # get users
    users = manager.get_active_users()
    print(f"Active users: {users}")

if __name__ == "__main__":
    asyncio.run(demo())
