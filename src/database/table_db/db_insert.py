"""
Database Insert Operations Module

This module provides functions for inserting data into the database tables:
- chunks: Document chunks and metadata
- query_responses: User queries and bot responses
- user_info: User registration information

All operations include comprehensive error handling and logging.
"""

import logging
import os
import sys
from typing import Dict, List, Tuple

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
from src.infra import setup_logging
from src.helpers import get_settings, Settings
from src.enums import InsertMsg

# Initialize application settings and logger
logger = setup_logging(name="TABLE-DATABASE")
app_settings: Settings = get_settings()


def insert_chunks(conn: sqlite3.Connection, chunks_data: List[Dict[str, str]]) -> bool:
    """
    Insert document chunks into the database.

    Args:
        conn: Active SQLite database connection
        chunks_data: List of dictionaries containing chunk data with keys:
                    - text: The chunk content
                    - pages: Page numbers (comma-separated)
                    - sources: Source documents (comma-separated)
                    - authors: Authors (comma-separated)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO chunks (text, pages, sources, authors)
            VALUES (:text, :pages, :sources, :authors)
            """,
            chunks_data,
        )
        conn.commit()
        logger.info(InsertMsg.CHUNK_INSERT_SUCCESS.value.format(len(chunks_data)))
        return True
    except sqlite3.Error as e:
        logger.error(InsertMsg.CHUNK_INSERT_ERROR.value.format(e))
        conn.rollback()
        return False


def insert_query_response(
    conn: sqlite3.Connection, user_id: str, query: str, response: str
) -> bool:
    """
    Insert a query-response pair into the database.

    Args:
        conn: Active SQLite database connection
        user_id: Unique identifier for the user
        query: User's query text
        response: Bot's response text

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO query_responses (user_id, query, response)
            VALUES (?, ?, ?)
            """,
            (user_id, query, response),
        )
        conn.commit()
        logger.info(InsertMsg.QUERY_RESPONSE_SUCCESS.value.format(user_id))
        return True
    except sqlite3.Error as e:
        logger.error(InsertMsg.QUERY_RESPONSE_ERROR.value.format(e))
        conn.rollback()
        return False


def insert_user(
    conn: sqlite3.Connection, name: str, email: str, score: int = 0
) -> bool:
    """
    Insert a new user into the database.

    Args:
        conn: Active SQLite database connection
        name: User's full name
        email: User's email address (must be unique)
        score: Initial user score (default: 0)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_info (name, email, score)
            VALUES (?, ?, ?)
            """,
            (name, email, score),
        )
        conn.commit()
        logger.info(InsertMsg.USER_INSERT_SUCCESS.value.format(email))
        return True
    except sqlite3.IntegrityError:
        logger.warning(InsertMsg.USER_DUPLICATE_ERROR.value.format(email))
        return False
    except sqlite3.Error as e:
        logger.error(InsertMsg.USER_INSERT_ERROR.value.format(e))
        conn.rollback()
        return False


def batch_insert_chunks(
    conn: sqlite3.Connection, chunks_data: List[Dict[str, str]]
) -> Tuple[int, int]:
    """
    Batch insert chunks with success/failure tracking.

    Args:
        conn: Active SQLite database connection
        chunks_data: List of chunk dictionaries

    Returns:
        Tuple: (success_count, failure_count)
    """
    success = 0
    failure = 0

    for chunk in chunks_data:
        if insert_chunks(conn, [chunk]):
            success += 1
        else:
            failure += 1

    logger.info(InsertMsg.BATCH_PROGRESS.value.format(success, failure))
    return (success, failure)


if __name__ == "__main__":
    # Example usage
    from src.database.table_db.db_engine import get_sqlite_engine

    # Initialize database connection
    conn = get_sqlite_engine()

    if conn:
        try:
            # Example: Insert a user
            insert_user(conn, "John Doe", "john@example.com", 85)

            # Example: Insert query response
            insert_query_response(
                conn,
                "user123",
                "What are the visa requirements?",
                "Visa requirements depend on your country of origin...",
            )

            # Example: Insert chunks
            chunks = [
                {
                    "text": "This is a document chunk about immigration...",
                    "pages": "1,2,3",
                    "sources": "immigration_guide.pdf",
                    "authors": "Department of State",
                },
                {
                    "text": "Another important document section...",
                    "pages": "5",
                    "sources": "visa_handbook.pdf",
                    "authors": "USCIS",
                },
            ]
            insert_chunks(conn, chunks)

        finally:
            conn.close()
