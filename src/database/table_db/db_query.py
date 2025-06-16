"""
Database Fetch Operations Module

Provides flexible functions for fetching data from SQLite database tables.
"""

# Initialize logger
import logging
import os
import sys
import sqlite3
from typing import List, Dict, Any, Optional


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
    columns: List[str] = None,
    where_clause: str = None,
    params: tuple = None,
    order_by: str = None,
    limit: int = None,
) -> List[Dict[str, Any]]:
    """
    Fetches all rows from a specified table with flexible query options.

    Args:
        conn: Active SQLite database connection
        table_name: Name of the table to query
        columns: List of columns to select (None for all columns)
        where_clause: WHERE clause without the 'WHERE' keyword
        params: Parameters for the WHERE clause
        order_by: ORDER BY clause without the keywords
        limit: Maximum number of rows to return

    Returns:
        List of dictionaries where keys are column names and values are row data

    Examples:
        # Get all columns from 'users'
        fetch_all_rows(conn, "users")

        # Get specific columns with filtering
        fetch_all_rows(conn, "users",
                      ["id", "name", "email"],
                      "status = ? AND score > ?",
                      ("active", 50),
                      "name ASC",
                      100)
    """
    try:
        cursor = conn.cursor()

        # Build SELECT clause
        select_columns = "*" if columns is None else ", ".join(columns)
        query = f"SELECT {select_columns} FROM {table_name}"

        # Add WHERE clause if provided
        if where_clause:
            query += f" WHERE {where_clause}"

        # Add ORDER BY if provided
        if order_by:
            query += f" ORDER BY {order_by}"

        # Add LIMIT if provided
        if limit:
            query += f" LIMIT {limit}"

        # Execute query
        logger.info(QueryMsg.FETCH_STARTED.value.format(table_name))

        cursor.execute(query, params or ())
        rows = cursor.fetchall()

        # Get column names
        if columns is None:
            columns = [desc[0] for desc in cursor.description]

        logger.info(QueryMsg.FETCH_COMPLETED.value.format(len(rows), table_name))

        # Convert rows to dictionaries
        return [dict(zip(columns, row)) for row in rows]

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


def fetch_single_row(
    conn: sqlite3.Connection,
    table_name: str,
    columns: List[str] = None,
    where_clause: str = None,
    params: tuple = None,
) -> Optional[Dict[str, Any]]:
    """
    Fetches a single row from the specified table.

    Args:
        conn: Active SQLite database connection
        table_name: Name of the table to query
        columns: List of columns to select (None for all columns)
        where_clause: WHERE clause without the 'WHERE' keyword
        params: Parameters for the WHERE clause

    Returns:
        Single row as dictionary or None if not found

    Raises:
        sqlite3.Error: For database-related errors
        ValueError: For invalid input parameters
    """
    try:
        result = fetch_all_rows(
            conn=conn,
            table_name=table_name,
            columns=columns,
            where_clause=where_clause,
            params=params,
            limit=1,
        )
        return result[0] if result else None
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


def fetch_column_values(
    conn: sqlite3.Connection, table_name: str, column: str, distinct: bool = True
) -> List[Any]:
    """
    Fetches all values from a single column.

    Args:
        conn: Active SQLite database connection
        table_name: Name of the table to query
        column: Name of the column to fetch
        distinct: Whether to return only distinct values

    Returns:
        List of values from the specified column
    """
    try:
        distinct_clause = "DISTINCT" if distinct else ""
        cursor = conn.cursor()
        cursor.execute(f"SELECT {distinct_clause} {column} FROM {table_name}")
        return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(QueryMsg.COLUMN_FETCH_ERROR.value.format(column, table_name, e))
        return []


if __name__ == "__main__":
    # Example usage
    from src.database.table_db.db_engine import get_sqlite_engine

    # Initialize database connection
    db_path = os.path.join(os.path.dirname(__file__), "tables.db")
    conn = get_sqlite_engine()

    if conn:
        try:
            # Example 1: Fetch all users
            users = fetch_all_rows(conn, "user_info")
            print("All users:", users)

            # Example 2: Fetch specific columns with filtering
            active_users = fetch_all_rows(
                conn,
                "user_info",
                columns=["id", "name", "email"],
                where_clause="score > ?",
                params=(50,),
                order_by="name ASC",
            )
            print("Active users:", active_users)

            # Example 3: Fetch single row
            user = fetch_single_row(
                conn,
                "user_info",
                where_clause="email = ?",
                params=("john@example.com",),
            )
            print("Single user:", user)

            # Example 4: Fetch column values
            emails = fetch_column_values(conn, "user_info", "email")
            print("All emails:", emails)

        finally:
            conn.close()
