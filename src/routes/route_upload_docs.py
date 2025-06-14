"""
File Upload API Module

This module provides FastAPI endpoints for handling file uploads with:
- Single or multiple file upload support
- File type validation
- Filename sanitization
- Secure file storage
- Comprehensive error handling

API Endpoints:
    POST /upload/ - Handles single file upload with validation
    POST /upload/multiple/ - Handles multiple file uploads with validation
"""

import os
import sys
import shutil
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings
from src.controllers import generate_unique_filename

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()

upload_route = APIRouter()

UPLOAD_DIR = app_settings.DOC_LOCATION_SAVE
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _save_uploaded_file(file: UploadFile, upload_dir: str) -> dict:
    """Helper function to save an uploaded file with validation."""
    sanitized_filename = generate_unique_filename(file.filename)
    file_extension = os.path.splitext(sanitized_filename)[1].lower().lstrip(".")

    if file_extension not in app_settings.FILE_TYPES:
        logger.warning("Attempted upload with disallowed file type: %s", file_extension)
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file_extension}"
        )

    file_location = os.path.join(upload_dir, sanitized_filename)
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info("File '%s' saved at '%s'", sanitized_filename, file_location)
        return {
            "filename": sanitized_filename,
            "saved_to": file_location,
            "size": os.path.getsize(file_location)
        }
    except OSError as e:
        logger.error("Failed to save uploaded file: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save the uploaded file."
        ) from e

@upload_route.post("/upload/")
async def upload_single_file(
    file: UploadFile = File(...)
):
    """
    Upload a single file to the server after validating its extension.

    Args:
        file: The file being uploaded.
        app_settings: Application configuration settings.

    Returns:
        JSONResponse: Response indicating success or failure.
    """
    try:
        file_info = _save_uploaded_file(file, UPLOAD_DIR)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "File uploaded successfully.",
                "file": file_info
            }
        )
    except HTTPException:
        raise
    except Exception as e:  # pylint: disable=broad-except
        logger.exception("Unexpected error during file upload: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during upload."
        ) from e

@upload_route.post("/upload/multiple/")
async def upload_multiple_files(
    files: List[UploadFile] = File(...)
):
    """
    Upload multiple files to the server after validating their extensions.

    Args:
        files: List of files being uploaded.
        app_settings: Application configuration settings.

    Returns:
        JSONResponse: Response indicating success/failure for each file.
    """
    results = {
        "successful": [],
        "failed": []
    }

    for file in files:
        try:
            file_info = _save_uploaded_file(file, UPLOAD_DIR)
            results["successful"].append({
                "original_filename": file.filename,
                **file_info
            })
        except HTTPException as e:
            results["failed"].append({
                "filename": file.filename,
                "error": e.detail,
                "status_code": e.status_code
            })
        except Exception as e:  # pylint: disable=broad-except
            logger.exception("Unexpected error during file upload: %s", e)
            results["failed"].append({
                "filename": file.filename,
                "error": "Internal server error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
            })

    return JSONResponse(
        status_code=status.HTTP_207_MULTI_STATUS,
        content={
            "message": "Batch upload processed",
            "results": results,
            "summary": {
                "total": len(files),
                "successful": len(results["successful"]),
                "failed": len(results["failed"])
            }
        }
    )
