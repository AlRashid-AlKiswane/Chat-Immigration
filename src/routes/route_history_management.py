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
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.history import ChatHistoryManager
from src.enums.value_enums import ModelProvider
from src.schema import ChatMessage
from src.infra import setup_logging
from src import get_chat_history

logger = setup_logging(name="ROUTE-HISTORY-MANAGEMENT")
history_router = APIRouter(
    prefix="/api/v1/history",
    tags=["History"],
    responses={HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

def format_error_response(message: str, error: str = None) -> dict:
    """Standard error response format"""
    return {
        "status": "error",
        "message": message,
        "error": str(error) if error else None
    }


@history_router.post(
    "/{user_id}/messages",
    status_code=status.HTTP_201_CREATED
)
async def add_message(
    user_id: str,
    message_data: ChatMessage,
    provider: ModelProvider,
    manager: ChatHistoryManager = Depends(get_chat_history)
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
            content=message_data.content,
            role=message_data.role,
            provider=provider,
            model_info=message_data.model_info,
            metadata=message_data.metadata
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


@history_router.get("/{user_id}/history")
async def get_history(
    user_id: str,
    limit: Optional[int] = None,
    since: Optional[datetime] = None,
    manager: ChatHistoryManager = Depends(get_chat_history)
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


@history_router.delete("/{user_id}/history")
async def clear_history(
    user_id: str,
    manager: ChatHistoryManager = Depends(get_chat_history)
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


@history_router.get("/users/active")
async def get_active_users(
    manager: ChatHistoryManager = Depends(get_chat_history)
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
