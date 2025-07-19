"""
File Naming Utility Module

This module provides functionality to generate unique, sanitized filenames with proper extensions.
It handles various edge cases and provides fallback mechanisms when filename generation fails.

Functions:
    generate_unique_filename: Creates a unique sanitized filename with timestamp and UUID suffix.
"""

import os
import sys
import logging
import re
import uuid
from pathlib import Path
from datetime import datetime

# Constants
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.infra.logger import setup_logging
from src.helpers import get_settings, Settings

from src.enums import FilePreprocessingMsg


# Initialize application settings and logger
app_settings: Settings = get_settings()
logger = setup_logging()


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique, sanitized filename with timestamp and UUID suffix.

    This function:
    1. Validates the input filename
    2. Extracts and validates the name and extension
    3. Sanitizes the filename by replacing special characters
    4. Adds a unique suffix with timestamp and short UUID
    5. Provides fallback mechanisms for error cases

    Args:
        original_filename: The original filename to process

    Returns:
        str: A new sanitized filename with unique suffix

    Raises:
        ValueError: If the input filename is invalid
    """
    try:
        # pylint: disable=logging-format-interpolation
        # Validate input
        if not original_filename or not isinstance(original_filename, str):
            logger.error(
                FilePreprocessingMsg.INVALID_INPUT.value.format(original_filename)
            )
            raise ValueError("Filename must be a non-empty string")

        # Check file type against allowed types
        if not any(original_filename.endswith(ext) for ext in app_settings.FILE_TYPES):
            logger.warning(
                FilePreprocessingMsg.UNSUPPORTED_TYPE.value.format(original_filename)
            )

        # Extract components
        path_obj = Path(original_filename)
        extension = path_obj.suffix
        # pylint: disable=redefined-outer-name
        name = path_obj.stem

        # Handle missing extension
        if not extension:
            logger.warning(
                FilePreprocessingMsg.MISSING_EXTENSION.value.format(original_filename)
            )
            extension = ".dat"  # Default fallback extension

        # Handle empty name
        if not name:
            logger.warning(FilePreprocessingMsg.EMPTY_NAME.value)
            name = "file"

        # Sanitize the name (replace special chars with underscore)
        cleaned_name = re.sub(r"[^\w]", "_", name).strip("_")
        if cleaned_name != name:
            logger.debug(
                FilePreprocessingMsg.NAME_SANITIZED.value.format(name, cleaned_name)
            )

        # Generate unique suffix (timestamp + short UUID)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = uuid.uuid4().hex[:8]
        unique_suffix = f"{timestamp}_{short_uuid}"

        # Construct new filename
        new_filename = f"{cleaned_name}_{unique_suffix}{extension}"
        logger.debug(
            FilePreprocessingMsg.FILENAME_GENERATED.value.format(
                new_filename, original_filename
            )
        )

        return new_filename

    except ValueError as ve:
        logger.error(FilePreprocessingMsg.VALIDATION_ERROR.value.format(ve))
        raise
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logger.error(FilePreprocessingMsg.GENERATION_ERROR.value.format(e))
        # Fallback filename generation
        fallback_name = (
            f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
            f"{uuid.uuid4().hex[:8]}.dat"
        )
        logger.warning(FilePreprocessingMsg.FALLBACK_USED.value.format(fallback_name))
        return fallback_name


if __name__ == "__main__":
    # Example usage
    test_filenames = [
        "my file.txt",
        "invalid@name.jpg",
        "",
        None,
        "noextension",
        "valid_name.pdf",
    ]

    for name in test_filenames:
        try:
            result = generate_unique_filename(name)
            print(f"Original: {name} -> Generated: {result}")
        except ValueError as e:
            print(f"Error processing '{name}': {str(e)}")
