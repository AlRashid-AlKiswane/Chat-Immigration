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
import sqlite3

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings

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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                pages TEXT NOT NULL,
                sources TEXT NOT NULL,
                authors TEXT NOT NULL
            );
        """)
        conn.commit()
        logger.info("Table 'chunks' created successfully.")
    except sqlite3.Error as e:
        logger.error("Error creating 'chunks' table: %s", e)
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS query_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        logger.info("Table 'query_responses' created successfully.")
    except sqlite3.Error as e:
        logger.error("Error creating 'query_responses' table: %s", e)
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                score INTEGER NOT NULL
            );
        """)
        conn.commit()
        logger.info("Table 'user_info' created successfully.")
    except sqlite3.Error as e:
        logger.error("Error creating 'user_info' table: %s", e)
        raise


if __name__ == "__main__":
    from src.database.table_db.db_engine import get_sqlite_engine
    conn = get_sqlite_engine()
    if conn:
        logger.info("Database initialized successfully")
        init_chunks_table(conn=conn)
        init_query_response_table(conn=conn)
        init_user_info_table(conn=conn)
        conn.close()
    else:
        logger.error("Failed to initialize database")
        sys.exit(1)
