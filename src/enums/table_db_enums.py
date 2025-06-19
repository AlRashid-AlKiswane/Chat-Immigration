""" """

from enum import Enum


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
    """
    Enum containing all database operation messages.
    Messages use %-formatting for direct logging compatibility.
    """
    
    # Connection and setup
    PATH_CONFIG_SUCCESS = "Main directory path configured: %s"
    """Logged when system path is successfully configured. %s = path"""
    
    PATH_CONFIG_FAILURE = "Failed to set up main directory path: %s"
    """Critical error when path setup fails. %s = error details"""
    
    # Query execution
    QUERY_EXECUTED = "Executing query: %s"
    """Debug message showing raw SQL query. %s = query text"""
    
    NO_RESULTS = "No results found for table: %s"
    """Debug message when query returns empty. %s = table name"""
    
    ROWS_FETCHED = "Fetched %d rows from table %s"
    """Info message after successful fetch. %d = row count, %s = table name"""
    
    # Cache operations
    CACHE_LOOKUP = "Cache lookup - user_id: %s, query: %.20s... %s"
    """Info message for cache checks. %s = user_id, %.20s = query, %s = status"""
    
    CACHE_FAILURE = "Cache lookup failed: %s"
    """Error message when cache check fails. %s = error details"""
    
    # Error handling
    INPUT_VALIDATION_ERROR = "Input validation error: %s"
    """Error message for invalid parameters. %s = error details"""
    
    DATABASE_ERROR = "Database error: %s"
    """Error message for SQLite operations. %s = error details"""
    
    UNEXPECTED_ERROR = "Unexpected error during fetch: %s"
    """Critical error for unhandled exceptions. %s = error details"""
    
    COLUMN_WARNING = "Column index out of range: %s"
    """Warning message for column access issues. %s = column name"""


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

class ClearMsg(Enum):
    """
    Standardized messages for table clearing operations with %s placeholders
    """
    INVALID_TABLE_NAME = "Invalid table name: %s"
    TABLE_CLEAR_STARTED = "Starting to clear table: %s"
    TABLE_CLEAR_SUCCESS = "Successfully cleared table: %s"
    CLEAR_OPERATION_ERROR = "Error clearing table '%s': %s"
    DB_INTEGRITY_ERROR = "Database integrity error while clearing '%s': %s"
    CURSOR_CLOSED = "Cursor closed for table: %s"
    CURSOR_ERROR = "Cursor error: %s"

    def __str__(self):
        return self.value

    def __mod__(self, other):
        """Enable % operator for formatting"""
        if isinstance(other, tuple):
            return self.value % other
        return self.value % (other,)