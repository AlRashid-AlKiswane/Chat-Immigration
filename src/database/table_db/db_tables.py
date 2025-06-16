"""
Database Initialization Module

This module provides functionality for initializing SQLite database tables
for an immigration chatbot application. It handles the creation of:

- chunks table: Stores document chunks with metadata
- query_responses table: Tracks user queries and bot responses
- user_info table: Stores user registration information

All database operations include comprehensive error handling and logging.
"""

import logging
import os
import sys

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import sqlite3

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
# pylint: disable=logging-format-interpolation
from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings
from src.enums import TablesMsg

# Initialize application settings and logger
logger = setup_logging()
app_settings: Settings = get_settings()


def init_chunks_table(conn: sqlite3.Connection) -> None:
    """
    Initialize the chunks table for storing document chunks and metadata.

    Args:
        conn: Active SQLite database connection

    Raises:
        sqlite3.Error: If table creation fails
    """
    try:
        logger.info(TablesMsg.TABLE_CREATE_STARTED.value)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                pages TEXT NOT NULL,
                sources TEXT NOT NULL,
                authors TEXT NOT NULL
            );
        """
        )
        conn.commit()
        logger.info(TablesMsg.TABLE_CREATE_SUCCESS.value.format("chunks"))
    except sqlite3.Error as e:
        logger.error(TablesMsg.TABLE_CREATE_FAILED.value.format("chunks", str(e)))
        raise


def init_query_response_table(conn: sqlite3.Connection) -> None:
    """
    Initialize the query_responses table for tracking user queries and responses.

    Args:
        conn: Active SQLite database connection

    Raises:
        sqlite3.Error: If table creation fails
    """
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS query_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """
        )
        conn.commit()
        logger.info(TablesMsg.TABLE_CREATE_SUCCESS.value.format("query_responses"))
    except sqlite3.Error as e:
        logger.error(
            TablesMsg.TABLE_CREATE_FAILED.value.format("query_responses", str(e))
        )
        raise


def init_user_info_table(conn: sqlite3.Connection) -> None:
    """
    Initialize the user_info table for storing user registration data.

    Args:
        conn: Active SQLite database connection

    Raises:
        sqlite3.Error: If table creation fails
    """
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                score INTEGER NOT NULL
            );
        """
        )
        conn.commit()
        logger.info(TablesMsg.TABLE_CREATE_SUCCESS.value.format("user_info"))
    except sqlite3.Error as e:
        logger.error(TablesMsg.TABLE_CREATE_FAILED.value.format("user_info", str(e)))
        raise


if __name__ == "__main__":
    from src.database.table_db.db_engine import get_sqlite_engine

    conn = get_sqlite_engine()
    if conn:
        logger.info(TablesMsg.DB_INIT_STARTED.value)
        init_chunks_table(conn=conn)
        init_query_response_table(conn=conn)
        init_user_info_table(conn=conn)
        logger.info(TablesMsg.DB_INIT_SUCCESS.value)
        conn.close()
        logger.info(TablesMsg.CONNECTION_CLOSED.value)
    else:
        logger.error(TablesMsg.DB_INIT_FAILED.value)
        sys.exit(1)
