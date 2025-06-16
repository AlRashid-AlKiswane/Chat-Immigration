"""
Database Fetch Operations Module

Provides flexible functions for fetching data from SQLite database tables.
"""

# Initialize logger
import logging
import os
import sys

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
import sqlite3
from typing import List, Dict, Any, Optional, Tuple, Union


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
from src.enums import QueryMsg

# Initialize application settings and logger
logger = setup_logging()
app_settings: Settings = get_settings()


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
def fetch_all_rows(
    conn: sqlite3.Connection,
    table_name: str,
    rely_data: str = "text",
    cach: Optional[Tuple[str, str]] = None,  # Tuple[user_id, query]
    columns: Optional[List[str]] = None,
) -> Union[List[Dict[str, Any]], Optional[str]]:
    """
    Pulls data from a specified table or retrieves a cached response.

    Args:
        conn (sqlite3.Connection): SQLite connection.
        table_name (str): Target table name.
        columns (List[str]): List of column names to select.
        rely_data (str): Key name for data in return dictionary.
        cach (Optional[Tuple[str, str]]): If set, retrieves cached response for (user_id, query).

    Returns:
        - List[Dict[str, Any]] for general table fetch.
        - str or None for cache mode (cached response).
    """
    try:
        cursor = conn.cursor()

        # Cache mode
        if cach:
            user_id, query = cach
            cursor.execute(
                "SELECT response FROM query_responses WHERE user_id = ? AND query = ?",
                (user_id, query)
            )
            row = cursor.fetchone()
            logger.info(f"[CACHE MODE] Queried cache for user_id={user_id}, query='{query}'. Found: {bool(row)}")
            return row[0] if row else None

        # General fetch mode
        else:
            cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
            rows = cursor.fetchall()
            logger.info(f"Pulled {len(rows)} row(s) from table '{table_name}'.")

            result = [
                {"id": row[columns.index("id")], rely_data: row[columns.index(rely_data)]} for row in rows
            ]
            return result

    except sqlite3.Error as e:
        logger.error(QueryMsg.DB_ERROR.value.format(e))
        return None
    except ValueError as e:
        logger.error(QueryMsg.INPUT_ERROR.value.format(e))
        return None
    except IndexError as e:
        logger.debug(QueryMsg.NO_RESULTS.value.format(e))
        return None
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(QueryMsg.UNEXPECTED_ERROR.value.format(e))
        return None
