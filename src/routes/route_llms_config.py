"""
LLM Configuration Router Module

This module provides FastAPI routes for configuring and managing different Large Language Model (LLM) providers.
It supports configuration for OpenAI, Cohere, DeepSeek, Gemini, and HuggingFace/local models.

The router handles model initialization, provider validation, and error handling for LLM configuration requests.
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
)
from src.logs.logger import setup_logging
from src.schema import ModelInfo
from src.llms import (
    CohereLLM,
    DeepSeekLLM,
    GeminiLLM,
    OpenAILLM,
    HuggingFaceLLM
)

llms_route = APIRouter()
setup_logging()

@llms_route.post("/llms/configure", response_class=JSONResponse)
async def configure_llm(
    request: Request,
    model_info: ModelInfo
) -> JSONResponse:
    """
    Configure the LLM provider and model to be used by the application.
    
    Args:
        request: FastAPI Request object for application state access
        model_info: Contains provider and model_name for the LLM configuration
        
    Returns:
        JSONResponse: Configuration success message or error details
        
    Raises:
        HTTPException: For various error scenarios with appropriate status codes
        
    Examples:
        >>> POST /llms/configure
        >>> {
        >>>     "provider": "openai",
        >>>     "model_name": "gpt-4"
        >>> }
    """
    try:
        logging.debug("Received LLM configuration request: %s", model_info.dict())

        provider = model_info.provider.lower()
        model_name = model_info.model_name

        logging.info("Attempting to configure %s model: %s", provider, model_name)

        # Initialize the appropriate LLM based on provider
        model: Any = None
        if provider == "openai":
            model = OpenAILLM(model_name=model_name)
        elif provider == "cohere":
            model = CohereLLM(model_name=model_name)
        elif provider == "deepseek":
            model = DeepSeekLLM(model_name=model_name)
        elif provider == "gemini":
            model = GeminiLLM(model_name=model_name)
        elif provider in ["huggingface", "local"]:
            model = HuggingFaceLLM(model_name=model_name)
        else:
            error_msg = f"Unsupported provider: {provider}"
            logging.warning(error_msg)
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Verify model initialization was successful
        if not model:
            error_msg = f"Failed to initialize model {model_name} from provider {provider}"
            logging.error(error_msg)
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )

        # Store the model in the application state
        request.app.state.model = model
        logging.info("Successfully configured %s model: %s", provider, model_name)

        response_data = {
            "message": "LLM configured successfully",
            "model_info": model.get_model_info(),
            "provider": provider,
            "model_name": model_name
        }

        logging.debug("Configuration response data: %s", response_data)
        return JSONResponse(
            status_code=HTTP_200_OK,
            content=response_data
        )

    except HTTPException:
        logging.warning("HTTPException raised during LLM configuration", exc_info=True)
        raise

    except ValueError as e:
        error_msg = f"Invalid configuration value: {str(e)}"
        logging.error(error_msg, exc_info=True)
        return HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    except ImportError as e:
        error_msg = f"Required dependencies not available: {str(e)}"
        logging.error(error_msg, exc_info=True)
        return HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    # pylint: disable=broad-exception-caught
    except Exception as e:
        error_msg = f"Unexpected error configuring LLM: {str(e)}"
        logging.critical(error_msg, exc_info=True)
        return HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
