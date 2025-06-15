""" """

from enum import Enum


class ClearMsg(Enum):
    """
    Database Clear Table Messages
    This class defines standardized log messages for database table clear using Enum classes.
    These messages ensure consistent logging across all database management components.
    """

    # --- Validation Messages ---
    INVALID_TABLE_NAME = "Invalid table name: '{}'"
    """Error when table name fails identifier validation."""

    TABLE_NOT_EXIST = "Table '{}' does not exist in schema"
    """Error when attempting operations on non-existent tables."""

    # --- Operation Messages ---
    TABLE_CLEAR_STARTED = "Preparing to clearing table '{}'"
    """Info message when table clearance begins."""

    TABLE_CLEAR_SUCCESS = "Successfully cleared '{}' ({} rows affected)"
    """Info message for successful table clearance."""

    # --- Error Messages ---
    CLEAR_OPERATION_ERROR = "Error clearing table '{}': {}"
    """Error when table clearance operation fails."""

    DB_INTEGRITY_ERROR = "Database integrity error: {}"
    """Error when constraints are violated."""

    # --- Cursor Messages ---
    CURSOR_CLOSED = "Cursor closed for table: {}"
    """Error when connection establishment fails."""

    CURSOR_ERROR = "Cursor operation failed: {}"
    """Error during cursor lifecycle operations."""


class EngineMsg(Enum):
    pass


class InsertMsg(Enum):
    pass


class QueryMsg(Enum):
    pass


class TablesMsg(Enum):
    pass
