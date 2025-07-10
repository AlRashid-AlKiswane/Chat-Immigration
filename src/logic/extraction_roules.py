"""
JSON Table Extraction Module

This module loads all cleaned JSON table files from the designated `assets/docs/table/`
directory, using the project-wide `load_json()` utility.

It applies strong logging, per-file error handling, and is designed for use in
preprocessing pipelines where multiple structured tables are parsed for rule extraction.

Author: AlRashid - Rama
Created: 2025-07-10
"""

import logging
import os
import sys
from typing import List, Dict, Any
import pandas as pd

# Setup main project directory for relative imports
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    if MAIN_DIR not in sys.path:
        sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("❌ Failed to set up main directory path: %s", e, exc_info=True)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs import setup_logging
from src.helpers import get_settings, Settings
from src.utils import load_json

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()

# Constants
TABLES_PATH = os.path.join(MAIN_DIR, "assets", "docs", "table")

def extraction_rules_from_json_tables() -> pd.DataFrame
    """
    Load all JSON files from the tables directory and return them as a list of dictionaries.

    Returns:
        List[Dict[str, Any]]: A list containing the parsed content of each JSON table.

    Raises:
        OSError: If the directory cannot be accessed.
    """
    tables: List[Dict[str, Any]] = []

    try:
        json_files = [f for f in os.listdir(TABLES_PATH) if f.lower().endswith(".json")]
        logger.info("📄 Found %d JSON files in '%s'", len(json_files), TABLES_PATH)
    except OSError as e:
        logger.error("❌ Failed to access directory '%s': %s", TABLES_PATH, e, exc_info=True)
        raise

    for json_file in json_files:
        full_path = os.path.join(TABLES_PATH, json_file)

        try:
            content = load_json(full_path)
            tables.append(content)
            logger.debug("✅ Loaded table: %s", json_file)
        except Exception as e:
            logger.warning("⚠️ Skipped file '%s' due to error: %s", json_file, e)

    logger.info("📊 Loaded %d JSON tables out of %d files", len(tables), len(json_files))
    return pd.DataFrame(tables)


# === CLI usage for test ===
if __name__ == "__main__":
    from pprint import pprint
    tables = extraction_rules_from_json_tables()
    pprint(tables)
