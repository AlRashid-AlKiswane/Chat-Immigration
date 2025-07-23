"""
SQLite Database Connection Module

This module provides robust functionality for creating and managing SQLite database connections
with comprehensive error handling and automatic directory creation.
"""

import logging
import os
import sys

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import sqlite3
from pathlib import Path
from typing import Optional

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
# pylint: disable=logging-format-interpolation
from src.infra.logger import setup_logging
from src.helpers import get_settings, Settings
from src.enums import EngineMsg

# Initialize application settings and logger
logger = setup_logging(name="TABLE-DATABASE")
app_settings: Settings = get_settings()


def get_sqlite_engine() -> Optional[sqlite3.Connection]:
    """
    Creates and returns a connection to an SQLite database with robust error handling.

    Returns:
        sqlite3.Connection: Database connection if successful
        None: If connection fails

    Raises:
        ValueError: For configuration issues
        sqlite3.Error: For database-specific errors
    """
    try:
        if not app_settings.SQLITE_DB:
            raise ValueError(EngineMsg.MISSING_DB_PATH.value)

        db_path = Path(app_settings.SQLITE_DB)
        db_dir = db_path.parent

        # Ensure directory exists with proper permissions
        try:
            db_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
            logger.debug(EngineMsg.DIR_CREATE_SUCCESS.value.format(db_dir))
        except PermissionError as pe:
            logger.error(EngineMsg.DIR_CREATE_FAILED.value.format(pe))
            raise sqlite3.OperationalError(f"Directory creation failed: {pe}") from pe

        # Verify directory is writable
        if not os.access(db_dir, os.W_OK):
            logger.error(EngineMsg.DIR_NOT_WRITABLE.value.format(db_dir))
            raise sqlite3.OperationalError(f"Directory not writable: {db_dir}")

        # Create database connection
        try:
            conn = sqlite3.connect(str(db_path))
            conn.execute("PRAGMA journal_mode=WAL")  # Enable Write-Ahead Logging
            logger.info(EngineMsg.CONNECT_SUCCESS.value.format(db_path))
            return conn
        except sqlite3.Error as se:
            logger.error(EngineMsg.CONNECT_FAILED.value.format(se))
            raise

    except ValueError as ve:
        logger.error(EngineMsg.CONFIG_ERROR.value.format(ve))
        raise
    except sqlite3.Error as se:
        logger.error(EngineMsg.DB_OPERATION_ERROR.value.format(se))
        raise
    except Exception as e:  # pylint: disable=broad-except
        logger.error(EngineMsg.UNEXPECTED_ERROR.value.format(e))
        return None


if __name__ == "__main__":
    conn = get_sqlite_engine()
    if conn:
        print(EngineMsg.CONNECT_SUCCESS.value)
        conn.close()
