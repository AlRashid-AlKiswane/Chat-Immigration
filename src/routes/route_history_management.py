"""
Enhanced Chat History API Endpoints with JSON Responses

This module provides RESTful endpoints for managing chat histories with:
- Consistent JSON response format
- Proper request validation
- Comprehensive error handling
- Clear API documentation
"""
import os
import sys
import logging
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from src.history import ChatHistoryManager
from src.enums.value_enums import ModelProvider
from src.schema import (
    HistMessageRequest,
    HistoryResponse,
    ProviderStatsResponse
)
from src.logs.logger import setup_logging

logger = setup_logging()
router = APIRouter(prefix="/chat/manage", tags=["chat_history"])


def get_chat_manager() -> ChatHistoryManager:
    """Dependency injection for chat history manager"""
    return ChatHistoryManager()


def format_error_response(message: str, error: str = None) -> dict:
    """Standard error response format"""
    return {
        "status": "error",
        "message": message,
        "error": str(error) if error else None
    }


@router.post(
    "/{user_id}/messages",
    status_code=status.HTTP_201_CREATED
)
async def add_message(
    user_id: str,
    request: HistMessageRequest,
    provider: ModelProvider,
    manager: ChatHistoryManager = Depends(get_chat_manager)
) -> JSONResponse:
    """
    Add a new message to user's chat history

    - **user_id**: Unique user identifier (required)
    - **provider**: AI model provider (required query param)
    - **content**: Message text (1-5000 chars)
    - **role**: Either 'user' or 'ai'
    - **model_info**: Required when role='ai'
    """
    try:
        message = await manager.add_message(
            user_id=user_id,
            content=request.content,
            role=request.role,
            provider=provider,
            model_info=request.model_info,
            metadata=request.metadata
        )

        history = await manager.get_history(user_id)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "status": "success",
                "data": {
                    "user_id": user_id,
                    "provider": provider,
                    "messages": [msg.model_dump() for msg in history.messages],
                    "count": len(history.messages)
                }
            }
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=format_error_response("Validation failed", e)
        )
    except Exception as e:
        logger.error(f"Failed to add message: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_error_response("Failed to add message", e)
        )


@router.get("/{user_id}/history")
async def get_history(
    user_id: str,
    limit: Optional[int] = None,
    since: Optional[datetime] = None,
    manager: ChatHistoryManager = Depends(get_chat_manager)
) -> JSONResponse:
    """
    Retrieve chat history with optional filters

    - **user_id**: Target user identifier
    - **limit**: Maximum messages to return
    - **since**: Only return messages after this timestamp
    """
    try:
        history = await manager.get_history(user_id, limit, since)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": {
                    "user_id": user_id,
                    "provider": history.provider,
                    "messages": [msg.model_dump() for msg in history.messages],
                    "count": len(history.messages)
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to retrieve history: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_error_response("Failed to retrieve history", e)
        )


@router.delete("/{user_id}/history")
async def clear_history(
    user_id: str,
    manager: ChatHistoryManager = Depends(get_chat_manager)
) -> JSONResponse:
    """Clear all chat history for a user"""
    try:
        await manager.clear_history(user_id)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "message": f"History cleared for user {user_id}"
            }
        )
    except Exception as e:
        logger.error(f"Failed to clear history: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_error_response("Failed to clear history", e)
        )


@router.get("/users/active")
async def get_active_users(
    manager: ChatHistoryManager = Depends(get_chat_manager)
) -> JSONResponse:
    """List all users with active chat histories"""
    try:
        users = manager.get_active_users()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": users,
                "count": len(users)
            }
        )
    except Exception as e:
        logger.error(f"Failed to get active users: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_error_response("Failed to retrieve active users", e)
        )
