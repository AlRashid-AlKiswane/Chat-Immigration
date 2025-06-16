"""
Database Table Management Module

Provides functions for safely clearing SQLite database tables with:
- Input validation
- Transaction management
- Comprehensive error handling
- Detailed logging
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
from src.enums import ClearMsg

# Initialize application settings and logger
logger = setup_logging()
app_settings: Settings = get_settings()


def clear_table(conn: sqlite3.Connection, table_name: str) -> None:
    """
    Clears all records from the specified SQLite table.

    Args:
        conn: An active database connection
        table_name: The name of the table to clear

    Raises:
        ValueError: If the table name contains invalid characters
        RuntimeError: If an error occurs during deletion
        sqlite3.Error: For database-specific errors
    """
    if not isinstance(table_name, str) or not table_name.isidentifier():
        error_msg = ClearMsg.INVALID_TABLE_NAME.value.format(table_name)
        logger.error(error_msg)
        raise ValueError(error_msg)

    cursor = None
    try:
        logger.debug(ClearMsg.TABLE_CLEAR_STARTED.value.format(table_name))
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        conn.commit()
        logger.info(ClearMsg.TABLE_CLEAR_SUCCESS.value.format(table_name))

    except sqlite3.OperationalError as e:
        error_msg = ClearMsg.CLEAR_OPERATION_ERROR.value.format(table_name, e)
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    except sqlite3.DatabaseError as e:
        error_msg = ClearMsg.DB_INTEGRITY_ERROR.value.format(table_name, e)
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e

    except Exception as e:  # pylint: disable=broad-except
        error_msg = ClearMsg.CLEAR_OPERATION_ERROR.value.format(table_name, e)
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from e

    finally:
        if cursor:
            try:
                cursor.close()
                logger.debug(ClearMsg.CURSOR_CLOSED.value.format(table_name))
            except sqlite3.Error as e:
                logger.warning(ClearMsg.CURSOR_ERROR.value.format(e))
