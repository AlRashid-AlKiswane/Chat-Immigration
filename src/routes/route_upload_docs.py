"""
File Upload API Module

This module provides a unified FastAPI endpoint for handling file uploads with:
- Support for one or many file uploads
- File type validation
- Filename sanitization
- Secure file storage
- Robust error logging and JSON responses

API Endpoint:
    POST /upload/ - Handles both single and multiple file uploads
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

from src.infra.logger import setup_logging
from src.helpers import get_settings, Settings
from src.controllers import generate_unique_filename
from src.enums import FileUploadMsg

logger = setup_logging(name="ROUTE-UPLOAD-DOCS")

app_settings: Settings = get_settings()
upload_route = APIRouter()
UPLOAD_DIR = app_settings.DOC_LOCATION_SAVE


def _save_uploaded_file(file: UploadFile, upload_dir: str) -> dict:
    """Helper function to save a validated and sanitized uploaded file."""
    sanitized_filename = generate_unique_filename(file.filename)
    file_extension = os.path.splitext(sanitized_filename)[1].lower().lstrip(".")

    if file_extension not in app_settings.FILE_TYPES:
        logger.warning(FileUploadMsg.INVALID_FILE_TYPE.value.format(file_extension))
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=FileUploadMsg.get_http_detail(
                FileUploadMsg.INVALID_FILE_TYPE, file_extension
            ),
        )

    file_location = os.path.join(upload_dir, sanitized_filename)
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(
            FileUploadMsg.FILE_SAVED.value.format(sanitized_filename, file_location)
        )
        return {
            "filename": sanitized_filename,
            "saved_to": file_location,
            "size": os.path.getsize(file_location),
        }
    except OSError as e:
        logger.error(FileUploadMsg.FILE_SAVE_ERROR.value.format(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=FileUploadMsg.get_http_detail(FileUploadMsg.FILE_SAVE_ERROR, str(e)),
        ) from e


@upload_route.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload one or more files to the server after validating their extensions.

    Args:
        files (List[UploadFile]): One or more files submitted via multipart/form-data.

    Returns:
        JSONResponse: JSON summary of upload results including success and failure details.
    """
    results = {"successful": [], "failed": []}

    for file in files:
        try:
            file_info = _save_uploaded_file(file, UPLOAD_DIR)
            results["successful"].append(
                {"original_filename": file.filename, **file_info}
            )
        except HTTPException as e:
            results["failed"].append(
                {
                    "filename": file.filename,
                    "error": e.detail,
                    "status_code": e.status_code,
                }
            )
        except Exception as e:
            logger.exception(FileUploadMsg.UPLOAD_ERROR.value.format(e))
            results["failed"].append(
                {
                    "filename": file.filename,
                    "error": "Internal server error",
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            )

    total = len(files)
    success = len(results["successful"])
    failed = len(results["failed"])

    log_msg = FileUploadMsg.MULTI_UPLOAD_SUCCESS.value.format(success, failed)
    logger.info(log_msg)

    return JSONResponse(
        status_code=status.HTTP_207_MULTI_STATUS,
        content={
            "message": log_msg,
            "results": results,
            "summary": {
                "total": total,
                "successful": success,
                "failed": failed,
            },
        },
    )
