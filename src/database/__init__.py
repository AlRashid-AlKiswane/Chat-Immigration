"""
Package Initialization File

This module initializes the Python package and provides access to core database 
functions related to chunk management, user interactions, and query-response 
logging for the application.

Modules Imported from `table_db`:
- get_sqlite_engine: Initializes and returns a SQLite engine instance.
- insert_chunks: Inserts document chunks into the database.
- insert_query_response: Logs user queries and LLM-generated responses.
- insert_user: Adds a new user entry to the user table.
- init_chunks_table: Creates or verifies the existence of the chunks table.
- init_query_response_table: Creates or verifies the query-response log table.
- init_user_info_table: Creates or verifies the user information table.
- fetch_all_rows: Retrieves all rows from a specified table.
- fetch_column_values: Fetches distinct values from a specific column.
- fetch_single_row: Retrieves a single row based on criteria.
- clear_table: Deletes all records from a given table.

This file allows the application to use core data handling functions in a clean and 
modular manner.

Typical usage example:
    from your_package_name import insert_chunks, fetch_all_rows
"""

from .table_db import (
    clear_table,
    fetch_all_rows,
    fetch_column_values,
    fetch_single_row,
    get_sqlite_engine,
    init_chunks_table,
    init_query_response_table,
    init_user_info_table,
    insert_chunks,
    insert_query_response,
    insert_user,
)
