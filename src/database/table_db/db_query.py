"""
Database Fetch Operations Module

Provides robust functions for fetching data from SQLite database tables with:
- Flexible querying capabilities
- Comprehensive error handling
- Caching functionality
- Detailed logging
"""

# pylint: disable=wrong-import-position
# Standard library imports
import logging
import os
import sys

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

# pylint: disable=logging-not-lazy
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
                    QueryMsg.CACHE_LOOKUP.value %
                    (user_id,
                    query,
                    "Found" if row else "Not found"
                ))
                return row[0] if row else None
            except sqlite3.Error as e:
                logger.error(QueryMsg.CACHE_FAILURE.value % str(e))
                return None

        # General query mode
        query = f"SELECT {', '.join(columns)} FROM {table_name}"
        params = []

        if where_clause:
            query += f" WHERE {where_clause}"

        if limit:
            query += f" LIMIT {limit}"

        logger.debug( QueryMsg.QUERY_EXECUTED.value % query)
        cursor.execute(query, params)
        rows = cursor.fetchall()

        if not rows:
            logger.debug(QueryMsg.NO_RESULTS.value % table_name)
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
                    logger.warning(QueryMsg.COLUMN_WARNING.value % col)
                    continue
            result.append(row_dict)

        logger.info(QueryMsg.ROWS_FETCHED.value % (len(result), table_name))
        return result

    except ValueError as e:
        logger.error(QueryMsg.INPUT_VALIDATION_ERROR.value % str(e))
        raise
    except sqlite3.Error as e:
        logger.error(QueryMsg.DATABASE_ERROR.value % str(e))
        raise
    except Exception as e:
        logger.exception(QueryMsg.UNEXPECTED_ERROR.value % str(e))
        raise

if __name__ == "__main__":
    from src.database import get_sqlite_engine

    conn: sqlite3.Connection = get_sqlite_engine()

    cache_result = fetch_all_rows(
        conn=conn,
        table_name="query_responses",
        columns=["user_id", "response", "query"],
        cache_key=("alrashid", "what is machine learning"),
        where_clause="user_id = 'alrashid' AND query = 'what is machine learning'"
    )
    if cache_result:
        print("Cache result found:", cache_result)
    else:
        print("No cache result found.")

