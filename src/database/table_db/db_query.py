"""
Database Fetch Operations Module

Provides robust functions for fetching data from SQLite database tables with:
- Flexible querying capabilities
- Comprehensive error handling
- Caching functionality
- Detailed logging
"""

# Standard library imports
import logging
import os
import sys
from typing import List, Dict, Any, Optional, Tuple, Union

# Third-party imports
import sqlite3

# Local application imports
from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings
from src.enums import QueryMsg

# Special SQLite configuration
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    sys.path.append(MAIN_DIR)
    logging.debug("Main directory path configured: %s", MAIN_DIR)
except (ImportError, OSError) as e:
    logging.critical("Failed to set up main directory path: %s", e, exc_info=True)
    sys.exit(1)

# Initialize application settings and logger
logger = setup_logging()
app_settings: Settings = get_settings()

def fetch_all_rows(
    conn: sqlite3.Connection,
    table_name: str,
    columns: Optional[List[str]] = None,
    rely_data: str = "text",
    cache_key: Optional[Tuple[str, str]] = None,
    where_clause: Optional[str] = None,
    limit: Optional[int] = None
) -> Union[List[Dict[str, Any]], Optional[str]]:
    """
    Fetches data from a database table with optional caching and filtering.

    Args:
        conn: Active SQLite database connection
        table_name: Name of the table to query
        columns: List of columns to select (None for all)
        rely_data: Key name for the data in returned dictionary
        cache_key: Tuple of (user_id, query) for cache lookup
        where_clause: Optional WHERE clause for filtering
        limit: Maximum number of rows to return

    Returns:
        - List of dictionaries for general queries
        - Single string response for cache lookups
        - None on error or no results

    Raises:
        ValueError: For invalid input parameters
        sqlite3.Error: For database-specific errors
    """
    try:
        # Validate inputs
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Invalid table name")
        
        if columns is None:
            columns = ["*"]
        elif not isinstance(columns, list):
            raise ValueError("Columns must be a list")

        cursor = conn.cursor()

        # Cache lookup mode
        if cache_key:
            user_id, query = cache_key
            try:
                cursor.execute(
                    "SELECT response FROM query_responses WHERE user_id = ? AND query = ?",
                    (user_id, query))
                row = cursor.fetchone()
                logger.info(
                    "Cache lookup - user_id: %s, query: %.20s... %s",
                    user_id,
                    query,
                    "Found" if row else "Not found"
                )
                return row[0] if row else None
            except sqlite3.Error as e:
                logger.error("Cache lookup failed: %s", e)
                return None

        # General query mode
        query = f"SELECT {', '.join(columns)} FROM {table_name}"
        params = []

        if where_clause:
            query += f" WHERE {where_clause}"
        
        if limit:
            query += f" LIMIT {limit}"

        logger.debug("Executing query: %s", query)
        cursor.execute(query, params)
        rows = cursor.fetchall()

        if not rows:
            logger.debug("No results found for table: %s", table_name)
            return []

        # Format results
        if columns == ["*"]:
            columns = [desc[0] for desc in cursor.description]

        result = []
        for row in rows:
            row_dict = {}
            for idx, col in enumerate(columns):
                try:
                    if col == rely_data:
                        row_dict[rely_data] = row[idx]
                    else:
                        row_dict[col] = row[idx]
                except IndexError:
                    logger.warning("Column index out of range: %s", col)
                    continue
            result.append(row_dict)

        logger.info("Fetched %d rows from table %s", len(result), table_name)
        return result

    except ValueError as e:
        logger.error("Input validation error: %s", e)
        raise
    except sqlite3.Error as e:
        logger.error("Database error: %s", e)
        raise
    except Exception as e:
        logger.exception("Unexpected error during fetch: %s", e)
        raise
