"""
LLM Configuration Router Module

This module provides FastAPI routes for configuring and 
    managing different Large Language llm (LLM) providers.
It supports configuration for OpenAI, Cohere, DeepSeek, Gemini, and HuggingFace/local llms.

The router handles llm initialization, provider validation,
 and error handling for LLM configuration requests.
"""

# pylint: disable=wrong-import-position
import logging
import os
import sys
from typing import Any

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
    logging.debug("Project base directory set to: %s", MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", str(e), exc_info=True)
    sys.exit(1)

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_404_NOT_FOUND
)
from src.infra import setup_logging
from src.schema import ModelInfo
from src.llms import (
    CohereLLM,
    DeepSeekLLM,
    GeminiLLM,
    OpenAILLM,
    # HuggingFaceLLM
)

llms_route = APIRouter(
    prefix="/api/v1/llms/config",
    tags=["LLMs"],
    responses={HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

logger = setup_logging(name="ROUTE-LLMS-CONFIG")

@llms_route.post("", response_class=JSONResponse)
async def configure_llm(
    request: Request,
    llm_info: ModelInfo
) -> JSONResponse:
    """
    Configure the LLM provider and llm to be used by the application.
    
    Args:
        request: FastAPI Request object for application state access
        llm_info: Contains provider and llm_name for the LLM configuration
        
    Returns:
        JSONResponse: Configuration success message or error details
        
    Raises:
        HTTPException: For various error scenarios with appropriate status codes
        
    Examples:
        >>> POST /llms/configure
        >>> {
        >>>     "provider": "openai",
        >>>     "llm_name": "gpt-4"
        >>> }
    """
    try:
        logger.debug("Received LLM configuration request: %s", llm_info.dict())

        provider = llm_info.provider.lower()
        llm_name = llm_info.model_name

        logger.info("Attempting to configure %s llm: %s", provider, llm_name)

        # Initialize the appropriate LLM based on provider
        llm: Any = None
        if provider == "openai":
            llm = OpenAILLM(model_name=llm_name)
        elif provider == "cohere":
            llm = CohereLLM(model_name=llm_name)
        elif provider == "deepseek":
            llm = DeepSeekLLM(model_name=llm_name)
        elif provider == "gemini":
            llm = GeminiLLM(model_name=llm_name)
        elif provider in ["huggingface", "local"]:
            llm = HuggingFaceLLM(model_name=llm_name)
        else:
            error_msg = f"Unsupported provider: {provider}"
            logger.warning(error_msg)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Verify llm initialization was successful
        if not llm:
            error_msg = f"Failed to initialize llm {llm_name} from provider {provider}"
            logger.error(error_msg)
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )

        # Store the llm in the application state
        request.app.state.llm = llm
        logger.info("Successfully configured %s llm: %s", provider, llm_name)

        response_data = {
            "message": "LLM configured successfully",
            "provider": provider,
            "llm_name": llm_name
        }

        logger.debug("Configuration response data: %s", response_data)
        return JSONResponse(
            status_code=HTTP_200_OK,
            content=response_data
        )

    except HTTPException:
        logger.warning("HTTPException raised during LLM configuration", exc_info=True)
        raise

    except ValueError as e:
        error_msg = f"Invalid configuration value: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    except ImportError as e:
        error_msg = f"Required dependencies not available: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    # pylint: disable=broad-exception-caught
    except Exception as e:
        error_msg = f"Unexpected error configuring LLM: {str(e)}"
        logger.critical(error_msg, exc_info=True)
        return HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
