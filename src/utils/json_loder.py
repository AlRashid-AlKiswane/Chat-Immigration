"""
JSON File Utility Module

This module provides utility functions for safely loading and cleaning JSON files.
It includes recursive whitespace removal from string values, detailed logging, 
and robust error handling. Intended for use in data pipelines, configuration 
loaders, or any application requiring JSON parsing.

Features:
- Supports both `str` and `Path` file inputs.
- Removes all whitespace from string values in nested structures.
- Full logging integration for success and failure.
- Raises detailed exceptions for common I/O and decoding errors.

Typical Usage:
    >>> from utils.load_json import load_json
    >>> config = load_json("config/settings.json")

Author: AlRashid - Rama
Created: 2025-07-10
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, Union

# Setup base project path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("❌ Failed to set up main directory path: %s", e, exc_info=True)
    sys.exit(1)

# Project imports (adjust as needed for your structure)
from src.logs import setup_logging
from src.helpers import get_settings, Settings

# Initialize logger and app settings
logger = setup_logging()
app_settings: Settings = get_settings()


def clean_json_keys_and_values(data):
    """
    Recursively clean keys and values in a JSON-like structure by:
    - Stripping all whitespace from both keys and string values.
    - Converting numeric-looking strings to int or float.
    - Extracting numbers from French strings (e.g., '3ans', '5ansouplus' → 3, 5).
    - Handling special phrases like 'aucune', 'moinsd\'unan' → 0.

    Args:
        data (Any): JSON-like structure.

    Returns:
        Any: Cleaned structure with normalized keys and values.
    """
    if isinstance(data, dict):
        cleaned_dict = {}
        for k, v in data.items():
            clean_key = "_".join(k.split()) if isinstance(k, str) else k
            cleaned_dict[clean_key] = clean_json_keys_and_values(v)
        return cleaned_dict

    elif isinstance(data, list):
        return [clean_json_keys_and_values(item) for item in data]

    elif isinstance(data, str):
        cleaned_val = "".join(data.split())

        # Handle French expressions
        if "aucune" in cleaned_val.lower() or "aucun" in cleaned_val.lower():
            return 0
        if "moinsd'unan" in cleaned_val.lower():
            return 0

        # Extract leading numeric portion
        match = re.match(r"^(\d+)", cleaned_val)
        if match:
            return int(match.group(1))

        # Try generic int/float
        if re.fullmatch(r'^-?\d+$', cleaned_val):
            return int(cleaned_val)
        elif re.fullmatch(r'^-?\d+\.\d+$', cleaned_val):
            return float(cleaned_val)

        return cleaned_val

    else:
        return data

def load_json(file: Union[str, Path]) -> Dict[str, Any]:
    """
    Load and parse a JSON file, then clean string values by removing whitespace.

    Args:
        file (Union[str, Path]): The path to the JSON file.

    Returns:
        Dict[str, Any]: Parsed and cleaned JSON content.

    Raises:
        ValueError: If file path is None or invalid.
        FileNotFoundError: If the file doesn't exist.
        json.JSONDecodeError: If the file is not valid JSON.
        OSError: For file read errors like permission denied.
    """
    if not file:
        logger.error("❌ No file path provided to load_json()")
        raise ValueError("JSON file path must be provided.")

    path = Path(file)

    if not path.is_file():
        logger.error("❌ File not found or is not a valid file: %s", path)
        raise FileNotFoundError(f"File not found: {path}")

    try:
        with path.open(mode="r", encoding="utf-8") as f:
            content = json.load(f)
            logger.debug("✅ Successfully loaded JSON from: %s", path)
            clear_content = clean_json_keys_and_values(content)
            return clear_content

    except json.JSONDecodeError as json_err:
        logger.error("❌ Failed to decode JSON from file %s: %s", path, json_err, exc_info=True)
        raise

    except OSError as os_err:
        logger.error("❌ OS error while reading file %s: %s", path, os_err, exc_info=True)
        raise


# === CLI Usage for Manual Testing ===
if __name__ == "__main__":
    from pprint import pprint

    # Example path (update to your actual test file)
    path = "/home/alrashid/Desktop/Chat-Immigration/assets/docs/table/www.canada.ca__en_immigration_refugees_citizenship_services_immigrate_canada_express_entry_check_score_crs_criteria_html_table_0.json"

    try:
        config = load_json(path)
        pprint(config)
    except Exception as e:
        print("❌ Error loading JSON config:", e)
