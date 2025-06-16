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
    """Standardized messages for SQLite database connection operations with format placeholders."""

    # --- Configuration Messages ---
    MISSING_DB_PATH = "Database path not configured in settings"
    """Critical error when SQLITE_DB setting is missing or empty."""

    INVALID_DB_PATH = "Invalid database path: {}"
    """Path validation failed. Rules: Must be absolute path with write permissions."""

    # --- Directory Operations ---
    DIR_CREATE_SUCCESS = "Verified database directory: {}"
    """Successfully created/verified directory with proper permissions (0o755)."""

    DIR_CREATE_FAILED = "Permission denied creating directory: {}"
    """OS-level permission error during directory creation."""

    DIR_NOT_WRITABLE = "Database directory not writable: {}"
    """Directory exists but application lacks write permissions."""

    # --- Connection Lifecycle ---
    CONNECT_STARTED = "Connecting to database: {}"
    """Initial connection attempt started to specified path."""

    CONNECT_SUCCESS = "Successfully connected to database: {}"
    """Connection established with PRAGMA journal_mode=WAL."""

    CONNECT_FAILED = "Database connection failed: {}"
    """SQLite operational error during connection."""

    # --- WAL Mode ---
    WAL_ENABLED = "Write-Ahead Logging enabled"
    """Successfully enabled WAL journal mode for better concurrency."""

    WAL_ERROR = "WAL mode activation failed"
    """Failed to set journal_mode=WAL (falling back to default mode)."""

    # --- Error Handling ---
    CONFIG_ERROR = "Configuration error: {}"
    """Invalid application settings detected."""

    DB_OPERATION_ERROR = "Database operation failed: {}"
    """SQLite-specific error during any database operation."""

    UNEXPECTED_ERROR = "Unexpected error: {}"
    """Non-database exception occurred during connection process."""


class InsertMsg(Enum):
    """Standardized messages for database insert operations with format placeholders."""

    # --- Chunk Operations ---
    CHUNK_INSERT_SUCCESS = "Inserted {} chunks successfully"
    """Successful insertion of document chunks. Table: chunks | Columns: text,pages,sources,authors"""

    CHUNK_INSERT_ERROR = "Error inserting chunks: {}"
    """SQLite error during chunk insertion. Failed rows: {failed_rows}"""

    # --- Query Response Operations ---
    QUERY_RESPONSE_SUCCESS = "Inserted query-response for user {}"
    """Logged user query and bot response. Table: query_responses"""

    QUERY_RESPONSE_ERROR = "Error inserting query-response: {}"
    """Failed to log query-response pair. User: {user_id} | Query length: {length}"""

    # --- User Operations ---
    USER_INSERT_SUCCESS = "Inserted new user: {}"
    """New user registration. Table: user_info | Columns: name,email,score"""

    USER_DUPLICATE_ERROR = "User with email {} already exists"
    """Integrity error on user insertion. Existing user ID: {existing_id}"""

    USER_INSERT_ERROR = "Error inserting user: {}"
    """General user insertion failure. Email attempted: {email}"""

    # --- Batch Operations ---
    BATCH_PROGRESS = "Batch progress: {} successful, {} failed"
    """Batch insertion status. Success: {success_count} | Failed: {failure_count} | Total: {total}"""


class QueryMsg(Enum):
    """Standardized messages for database query operations with format placeholders."""

    # --- Query Execution ---
    FETCH_STARTED = "Executing query on table '{}'"
    """Query initiated for table. Columns: {columns} | Filters: {where_clause}"""

    FETCH_COMPLETED = "Fetched {} rows from table '{}'"
    """Query completed successfully. Duration: {duration_ms}ms"""

    # --- Error Messages ---
    DB_ERROR = "Database error in {}: {}"
    """SQLite error occurred. Operation: {operation} | Error code: {error_code}"""

    INPUT_ERROR = "Invalid input in {}: {}"
    """Value error occurred. Parameter: {parameter} | Expected type: {expected_type}"""

    NO_RESULTS = "No results found in {}"
    """Empty result set. Table: {table} | Query: {query}"""

    UNEXPECTED_ERROR = "Unexpected error in {}: {}"
    """Unhandled exception. Type: {error_type} | Trace: {traceback}"""

    COLUMN_FETCH_ERROR = "Error fetching column '{}' from '{}': {}"
    """Column access failed. Valid columns: {valid_columns}"""


class TablesMsg(Enum):
    """Standardized messages for database initialization operations with format placeholders."""

    # --- Table Creation ---
    TABLE_CREATE_STARTED = "Starting creation of table '{}'"
    """Initializing table structure. Columns: {columns}"""

    TABLE_CREATE_SUCCESS = "Table '{}' created successfully"
    """Table schema: {schema}"""

    TABLE_CREATE_FAILED = "Error creating table '{}': {}"
    """Error type: {error_type} | SQL: {sql}"""

    # --- Database Setup ---
    DB_INIT_STARTED = "Database initialization started"
    """Database path: {db_path} | Tables to create: {tables}"""

    DB_INIT_SUCCESS = "Database initialized successfully"
    """Tables created: {created_tables} | Duration: {duration_sec:.2f}s"""

    DB_INIT_FAILED = "Database initialization failed: {}"
    """Failed tables: {failed_tables} | Error: {error_details}"""

    # --- Schema Verification ---
    TABLE_EXISTS = "Table '{}' already exists"
    """Existing schema hash: {schema_hash}"""

    SCHEMA_MISMATCH = "Schema mismatch in table '{}'"
    """Expected: {expected_schema} | Found: {actual_schema}"""

    # --- System Messages ---
    CONNECTION_ESTABLISHED = "Database connection established"
    """Connection ID: {conn_id} | Isolation level: {isolation_level}"""

    CONNECTION_CLOSED = "Database connection closed"
    """Duration open: {duration_min:.1f} minutes"""
