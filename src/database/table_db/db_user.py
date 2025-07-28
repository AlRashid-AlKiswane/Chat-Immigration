"""
Express Entry Assessment Database Management Module.

This module provides comprehensive database operations for managing Express Entry
assessment submissions. It includes functions for creating tables, inserting
assessment data, and retrieving stored information with full error handling
and logging capabilities.

The module uses SQLite as the database backend and provides the following
main functionalities:
- Creating the user_submissions table structure
- Inserting new assessment data with UUID generation
- Retrieving individual assessments by submission ID
- Fetching all assessments with pagination support

All functions include comprehensive error handling, input validation,
and detailed logging at multiple levels (DEBUG, INFO, WARNING, ERROR).

Author: System
Created: 2025
Python Version: 3.8+
Dependencies: sqlite3, uuid, logging
"""

from datetime import datetime
import logging
import os
import sys
import sqlite3
import uuid
from typing import Dict, List, Optional, Any

from fastapi import HTTPException

# SQLite module replacement for compatibility
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

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
from src.enums import TablesMsg

# Initialize application settings and logger
logger = setup_logging(name="USER-DATABASE")


def submit_assessment_table(conn: sqlite3.Connection) -> bool:
    """
    Create the user_submissions table for Express Entry assessments.
    
    This function creates a comprehensive table structure to store all
    Express Entry assessment data including personal information, education,
    language test scores, work experience, and spouse information.
    
    Args:
        conn (sqlite3.Connection): Active SQLite database connection object.
            Must be a valid, open connection to the target database.
    
    Returns:
        bool: True if table creation is successful, False otherwise.
    
    Raises:
        sqlite3.Error: If database operation fails.
        TypeError: If connection parameter is invalid.
        ValueError: If connection is closed or invalid.
    
    Example:
        >>> import sqlite3
        >>> conn = sqlite3.connect('assessments.db')
        >>> success = submit_assessment_table(conn)
        >>> if success:
        ...     print("Table created successfully")
        >>> conn.close()
    
    Note:
        - Uses IF NOT EXISTS to prevent errors if table already exists
        - All fields are nullable except id and submission_id
        - Includes automatic timestamp generation
        - Table structure supports conditional fields based on form logic
    """
    logger.info("Starting user_submissions table creation process")
    
    try:
        # Validate connection parameter
        if not isinstance(conn, sqlite3.Connection):
            logger.error("Invalid connection type provided: %s", type(conn))
            raise TypeError(f"Expected sqlite3.Connection, got {type(conn)}")
        
        # Check if connection is open
        try:
            conn.execute("SELECT 1")
        except sqlite3.ProgrammingError as e:
            logger.error("Database connection is closed or invalid: %s", e)
            raise ValueError("Database connection is closed or invalid") from e
        
        logger.debug("Database connection validated successfully")
        
        cursor = conn.cursor()
        logger.debug("Database cursor created")
        
        # Define table creation SQL with comprehensive structure
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS user_submissions (
                user_name TEXT PRIMARY KEY,
                submission_id TEXT UNIQUE NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                marital_status TEXT,
                age INTEGER,
                spouse_citizen TEXT,
                spouse_coming TEXT,
                education_level TEXT,
                canada_education TEXT,
                education_eca TEXT,
                language_test_recent TEXT,
                first_language_test TEXT,
                first_language_scores_listening TEXT,
                first_language_scores_speaking TEXT,
                first_language_scores_reading TEXT,
                first_language_scores_writing TEXT,
                second_language_test TEXT,
                second_language_scores_listening TEXT,
                second_language_scores_speaking TEXT,
                second_language_scores_reading TEXT,
                second_language_scores_writing TEXT,
                canadian_work_experience TEXT,
                foreign_work_experience TEXT,
                trade_certificate TEXT,
                job_offer TEXT,
                noc_teer TEXT,
                do_have_nomination TEXT,
                siblings TEXT,
                spouse_education TEXT,
                spouse_experience TEXT,
                spouse_language_test TEXT,
                spouse_language_scores_listening TEXT,
                spouse_language_scores_speaking TEXT,
                spouse_language_scores_reading TEXT,
                spouse_language_scores_writing TEXT
            )
        """
        
        logger.debug("Executing table creation SQL")
        cursor.execute(create_table_sql)
        
        logger.debug("Committing table creation transaction")
        conn.commit()
        
        logger.info("user_submissions table created successfully")
        return True
        
    except sqlite3.Error as e:
        logger.error("SQLite error during table creation: %s", e)
        try:
            conn.rollback()
            logger.debug("Transaction rolled back due to error")
        except sqlite3.Error as rollback_error:
            logger.error("Failed to rollback transaction: %s", rollback_error)
        return False
        
    except (TypeError, ValueError) as e:
        logger.error("Parameter validation error: %s", e)
        return False
        
    except Exception as e:
        logger.error("Unexpected error during table creation: %s", e)
        try:
            conn.rollback()
            logger.debug("Transaction rolled back due to unexpected error")
        except sqlite3.Error as rollback_error:
            logger.error("Failed to rollback transaction: %s", rollback_error)
        return False


def insert_assessment_data(user_name: str = None,
                          conn: sqlite3.Connection = None, 
                         assessment_data: Dict[str, Any] = None) -> Optional[str]:
    """
    Insert assessment data into the user_submissions table.
    
    This function validates and inserts a complete assessment record into
    the database. It generates a unique submission ID and handles all
    assessment fields including optional spouse and language test data.
    
    Args:
        conn (sqlite3.Connection): Active SQLite database connection object.
        assessment_data (Dict[str, Any]): Dictionary containing assessment data
            with keys corresponding to form field names. All values are optional
            and will be handled gracefully if missing.
    
    Returns:
        Optional[str]: Generated submission UUID if successful, None if failed.
    
    Raises:
        sqlite3.Error: If database operation fails.
        TypeError: If parameters are invalid types.
        ValueError: If connection is closed or data is severely malformed.
    
    Example:
        >>> data = {
        ...     'marital_status': 'married',
        ...     'age': 30,
        ...     'education_level': 'bachelor_or_three_year_post_secondary_or_more'
        ... }
        >>> submission_id = insert_assessment_data(conn, data)
        >>> if submission_id:
        ...     print(f"Assessment saved with ID: {submission_id}")
    
    Note:
        - Generates UUID4 for unique submission identification
        - Handles missing fields gracefully with None values
        - Uses parameterized queries to prevent SQL injection
        - Commits transaction automatically on success
    """
    logger.info("Starting assessment data insertion process")
    
    try:
        # Validate connection parameter
        if not isinstance(conn, sqlite3.Connection):
            logger.error("Invalid connection type: %s", type(conn))
            raise TypeError(f"Expected sqlite3.Connection, got {type(conn)}")
        
        # Validate assessment_data parameter
        if not isinstance(assessment_data, dict):
            logger.error("Invalid assessment_data type: %s", type(assessment_data))
            raise TypeError(f"Expected dict, got {type(assessment_data)}")
        
        if not assessment_data:
            logger.warning("Empty assessment data provided")
            return None
        
        # Check connection validity
        try:
            conn.execute("SELECT 1")
        except sqlite3.ProgrammingError as e:
            logger.error("Database connection is invalid: %s", e)
            raise ValueError("Database connection is closed or invalid") from e
        
        logger.debug("Parameters validated successfully")
        logger.debug("Assessment data keys: %s", list(assessment_data.keys()))
        
        cursor = conn.cursor()
        submission_id = str(uuid.uuid4())
        logger.info("Generated submission ID: %s", submission_id)
        
        # Prepare comprehensive data mapping with safe extraction
        data = {
            'user_name': user_name,
            'submission_id': submission_id,
            'marital_status': assessment_data.get('marital_status'),
            'age': assessment_data.get('age'),
            'spouse_citizen': assessment_data.get('spouse_citizen'),
            'spouse_coming': assessment_data.get('spouse_coming'),
            'education_level': assessment_data.get('education_level'),
            'canada_education': assessment_data.get('canada_education'),
            'education_eca': assessment_data.get('education_eca'),
            'language_test_recent': assessment_data.get('language_test_recent'),
            'first_language_test': assessment_data.get('first_language_test'),
            'first_language_scores_listening': assessment_data.get(
                'first_language_scores_listening'
            ),
            'first_language_scores_speaking': assessment_data.get(
                'first_language_scores_speaking'
            ),
            'first_language_scores_reading': assessment_data.get(
                'first_language_scores_reading'
            ),
            'first_language_scores_writing': assessment_data.get(
                'first_language_scores_writing'
            ),
            'second_language_test': assessment_data.get('second_language_test'),
            'second_language_scores_listening': assessment_data.get(
                'second_language_scores_listening'
            ),
            'second_language_scores_speaking': assessment_data.get(
                'second_language_scores_speaking'
            ),
            'second_language_scores_reading': assessment_data.get(
                'second_language_scores_reading'
            ),
            'second_language_scores_writing': assessment_data.get(
                'second_language_scores_writing'
            ),
            'canadian_work_experience': assessment_data.get(
                'canadian_work_experience'
            ),
            'foreign_work_experience': assessment_data.get(
                'foreign_work_experience'
            ),
            'trade_certificate': assessment_data.get('trade_certificate'),
            'job_offer': assessment_data.get('job_offer'),
            'noc_teer': assessment_data.get('noc_teer'),
            'do_have_nomination': assessment_data.get('do_have_nomination'),
            'siblings': assessment_data.get('siblings'),
            'spouse_education': assessment_data.get('spouse_education'),
            'spouse_experience': assessment_data.get('spouse_experience'),
            'spouse_language_test': assessment_data.get('spouse_language_test'),
            'spouse_language_scores_listening': assessment_data.get(
                'spouse_language_scores_listening'
            ),
            'spouse_language_scores_speaking': assessment_data.get(
                'spouse_language_scores_speaking'
            ),
            'spouse_language_scores_reading': assessment_data.get(
                'spouse_language_scores_reading'
            ),
            'spouse_language_scores_writing': assessment_data.get(
                'spouse_language_scores_writing'
            )
        }
        
        logger.debug("Data mapping completed with %d fields", len(data))
        
        # Create parameterized INSERT query for security
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        
        query = f"""
            INSERT INTO user_submissions ({columns})
            VALUES ({placeholders})
        """
        
        logger.debug("Executing INSERT query with %d parameters", len(data))
        cursor.execute(query, list(data.values()))
        
        logger.debug("Committing insertion transaction")
        conn.commit()
        
        logger.info("Assessment data inserted successfully with ID: %s", 
                   submission_id)
        return submission_id
        
    except sqlite3.IntegrityError as e:
        logger.error("Database integrity error during insertion: %s", e)
        try:
            conn.rollback()
            logger.debug("Transaction rolled back due to integrity error")
        except sqlite3.Error as rollback_error:
            logger.error("Failed to rollback transaction: %s", rollback_error)
        return None
        
    except sqlite3.Error as e:
        logger.error("SQLite error during data insertion: %s", e)
        try:
            conn.rollback()
            logger.debug("Transaction rolled back due to SQLite error")
        except sqlite3.Error as rollback_error:
            logger.error("Failed to rollback transaction: %s", rollback_error)
        return None
        
    except (TypeError, ValueError) as e:
        logger.error("Parameter validation error: %s", e)
        return None
        
    except Exception as e:
        logger.error("Unexpected error during data insertion: %s", e)
        try:
            conn.rollback()
            logger.debug("Transaction rolled back due to unexpected error")
        except sqlite3.Error as rollback_error:
            logger.error("Failed to rollback transaction: %s", rollback_error)
        return None


def get_assessment_by_id(conn: sqlite3.Connection, 
                        submission_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve assessment data by submission ID.
    
    This function fetches a complete assessment record from the database
    using the unique submission ID. It returns all stored fields as a
    dictionary for easy access and manipulation.
    
    Args:
        conn (sqlite3.Connection): Active SQLite database connection object.
        submission_id (str): Unique submission identifier (UUID format).
            Must be a valid UUID string as generated by insert_assessment_data.
    
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing all assessment fields
            if found, None if not found or error occurs. Keys correspond to
            database column names.
    
    Raises:
        sqlite3.Error: If database operation fails.
        TypeError: If parameters are invalid types.
        ValueError: If connection is closed or submission_id is invalid format.
    
    Example:
        >>> assessment = get_assessment_by_id(conn, "123e4567-e89b-12d3-a456-426614174000")
        >>> if assessment:
        ...     print(f"Age: {assessment['age']}")
        ...     print(f"Marital Status: {assessment['marital_status']}")
        >>> else:
        ...     print("Assessment not found")
    
    Note:
        - Returns None for non-existent submissions (not an error)
        - All database fields are included in returned dictionary
        - Uses parameterized query to prevent SQL injection
        - Includes comprehensive input validation
    """
    logger.info("Starting assessment retrieval for ID: %s", submission_id)
    
    try:
        # Validate connection parameter
        if not isinstance(conn, sqlite3.Connection):
            logger.error("Invalid connection type: %s", type(conn))
            raise TypeError(f"Expected sqlite3.Connection, got {type(conn)}")
        
        # Validate submission_id parameter
        if not isinstance(submission_id, str):
            logger.error("Invalid submission_id type: %s", type(submission_id))
            raise TypeError(f"Expected str, got {type(submission_id)}")
        
        if not submission_id.strip():
            logger.error("Empty or whitespace-only submission_id provided")
            raise ValueError("submission_id cannot be empty")
        
        # Basic UUID format validation
        submission_id = submission_id.strip()
        try:
            uuid.UUID(submission_id)
        except ValueError as e:
            logger.warning("Invalid UUID format for submission_id: %s", e)
            # Continue anyway - might be a different ID format
        
        # Check connection validity
        try:
            conn.execute("SELECT 1")
        except sqlite3.ProgrammingError as e:
            logger.error("Database connection is invalid: %s", e)
            raise ValueError("Database connection is closed or invalid") from e
        
        logger.debug("Parameters validated successfully")
        
        cursor = conn.cursor()
        
        # Execute parameterized SELECT query
        logger.debug("Executing SELECT query for submission_id: %s", 
                    submission_id)
        cursor.execute("""
            SELECT * FROM user_submissions 
            WHERE submission_id = ?
        """, (submission_id,))
        
        row = cursor.fetchone()
        
        if not row:
            logger.info("No assessment found for submission_id: %s", 
                       submission_id)
            return None
        
        # Get column names for dictionary creation
        columns = [description[0] for description in cursor.description]
        logger.debug("Retrieved %d columns from database", len(columns))
        
        # Convert row tuple to dictionary
        result = dict(zip(columns, row))
        
        logger.info("Assessment retrieved successfully for ID: %s", 
                   submission_id)
        logger.debug("Retrieved assessment fields: %s", list(result.keys()))
        
        return result
        
    except sqlite3.Error as e:
        logger.error("SQLite error during assessment retrieval: %s", e)
        return None
        
    except (TypeError, ValueError) as e:
        logger.error("Parameter validation error: %s", e)
        return None
        
    except Exception as e:
        logger.error("Unexpected error during assessment retrieval: %s", e)
        return None


def get_all_assessments(conn: sqlite3.Connection, 
                       limit: int = 100, 
                       offset: int = 0) -> Optional[List[Dict[str, Any]]]:
    """
    Get all assessment submissions with pagination support.
    
    This function retrieves multiple assessment records from the database
    with support for pagination. Records are ordered by timestamp in
    descending order (newest first) for optimal user experience.
    
    Args:
        conn (sqlite3.Connection): Active SQLite database connection object.
        limit (int, optional): Maximum number of records to return.
            Must be positive integer. Defaults to 100. Maximum recommended: 1000.
        offset (int, optional): Number of records to skip for pagination.
            Must be non-negative integer. Defaults to 0.
    
    Returns:
        Optional[List[Dict[str, Any]]]: List of dictionaries containing
            assessment data if successful, None if error occurs. Empty list
            if no records found (not an error condition).
    
    Raises:
        sqlite3.Error: If database operation fails.
        TypeError: If parameters are invalid types.
        ValueError: If connection is closed or pagination parameters invalid.
    
    Example:
        >>> # Get first 50 assessments
        >>> assessments = get_all_assessments(conn, limit=50, offset=0)
        >>> if assessments is not None:
        ...     print(f"Found {len(assessments)} assessments")
        ...     for assessment in assessments:
        ...         print(f"ID: {assessment['submission_id']}")
        >>> 
        >>> # Get next 50 assessments
        >>> next_batch = get_all_assessments(conn, limit=50, offset=50)
    
    Note:
        - Results ordered by timestamp DESC (newest first)
        - Returns empty list (not None) when no records found
        - Supports large datasets through pagination
        - All database fields included in each record
        - Validates pagination parameters for safety
    """
    logger.info("Starting bulk assessment retrieval with limit=%d, offset=%d", 
               limit, offset)
    
    try:
        # Validate connection parameter
        if not isinstance(conn, sqlite3.Connection):
            logger.error("Invalid connection type: %s", type(conn))
            raise TypeError(f"Expected sqlite3.Connection, got {type(conn)}")
        
        # Validate pagination parameters
        if not isinstance(limit, int):
            logger.error("Invalid limit type: %s", type(limit))
            raise TypeError(f"Expected int for limit, got {type(limit)}")
        
        if not isinstance(offset, int):
            logger.error("Invalid offset type: %s", type(offset))
            raise TypeError(f"Expected int for offset, got {type(offset)}")
        
        if limit <= 0:
            logger.error("Invalid limit value: %d (must be positive)", limit)
            raise ValueError("limit must be positive integer")
        
        if offset < 0:
            logger.error("Invalid offset value: %d (must be non-negative)", 
                        offset)
            raise ValueError("offset must be non-negative integer")
        
        if limit > 10000:
            logger.warning("Large limit value: %d (consider smaller batches)", 
                          limit)
        
        # Check connection validity
        try:
            conn.execute("SELECT 1")
        except sqlite3.ProgrammingError as e:
            logger.error("Database connection is invalid: %s", e)
            raise ValueError("Database connection is closed or invalid") from e
        
        logger.debug("Parameters validated successfully")
        
        cursor = conn.cursor()
        
        # Execute paginated SELECT query with ordering
        logger.debug("Executing paginated SELECT query")
        cursor.execute("""
            SELECT * FROM user_submissions 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        logger.debug("Retrieved %d rows from database", len(rows))
        
        if not rows:
            logger.info("No assessments found with current pagination parameters")
            return []
        
        # Get column names for dictionary creation
        columns = [description[0] for description in cursor.description]
        logger.debug("Processing %d columns per row", len(columns))
        
        # Convert all rows to list of dictionaries
        results = [dict(zip(columns, row)) for row in rows]
        
        logger.info("Successfully retrieved %d assessments", len(results))
        
        return results
        
    except sqlite3.Error as e:
        logger.error("SQLite error during bulk retrieval: %s", e)
        return None
        
    except (TypeError, ValueError) as e:
        logger.error("Parameter validation error: %s", e)
        return None
        
    except Exception as e:
        logger.error("Unexpected error during bulk retrieval: %s", e)
        return None


def get_assessment_count(conn: sqlite3.Connection) -> Optional[int]:
    """
    Get total count of assessments in the database.
    
    This utility function returns the total number of assessment records
    stored in the database. Useful for pagination calculations and
    system monitoring.
    
    Args:
        conn (sqlite3.Connection): Active SQLite database connection object.
    
    Returns:
        Optional[int]: Total number of assessment records if successful,
            None if error occurs. Returns 0 for empty table (not an error).
    
    Raises:
        sqlite3.Error: If database operation fails.
        TypeError: If connection parameter is invalid type.
        ValueError: If connection is closed or invalid.
    
    Example:
        >>> total = get_assessment_count(conn)
        >>> if total is not None:
        ...     print(f"Total assessments: {total}")
        ...     pages = (total + 99) // 100  # Calculate pages for limit=100
        ...     print(f"Total pages: {pages}")
    
    Note:
        - Very efficient operation using COUNT(*)
        - Returns 0 for empty table (valid result)
        - Useful for pagination UI and monitoring
    """
    logger.info("Getting total assessment count from database")
    
    try:
        # Validate connection parameter
        if not isinstance(conn, sqlite3.Connection):
            logger.error("Invalid connection type: %s", type(conn))
            raise TypeError(f"Expected sqlite3.Connection, got {type(conn)}")
        
        # Check connection validity
        try:
            conn.execute("SELECT 1")
        except sqlite3.ProgrammingError as e:
            logger.error("Database connection is invalid: %s", e)
            raise ValueError("Database connection is closed or invalid") from e
        
        logger.debug("Connection validated successfully")
        
        cursor = conn.cursor()
        
        # Execute COUNT query
        logger.debug("Executing COUNT query")
        cursor.execute("SELECT COUNT(*) FROM user_submissions")
        
        result = cursor.fetchone()
        count = result[0] if result else 0
        
        logger.info("Total assessment count: %d", count)
        
        return count
        
    except sqlite3.Error as e:
        logger.error("SQLite error during count operation: %s", e)
        return None
        
    except (TypeError, ValueError) as e:
        logger.error("Parameter validation error: %s", e)
        return None
        
    except Exception as e:
        logger.error("Unexpected error during count operation: %s", e)
        return None

def create_auth_user_table(conn: sqlite3.Connection) -> None:
    """
    Creates the user_auth table if it does not already exist.

    Args:
        conn (sqlite3.Connection): SQLite database connection.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_auth (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT UNIQUE NOT NULL,
                hashed_pass TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone_number TEXT,
                time_registered TEXT NOT NULL,
                is_superuser INTEGER DEFAULT 0  -- 0 = normal user, 1 = superuser
            )
        """)
        conn.commit()
        logger.info("user_auth table is ready.")
    except Exception as e:
        logger.critical("Failed to create user_auth table.", exc_info=True)
        raise


def fetch_auth_user(user_name: str, conn: sqlite3.Connection) -> Optional[dict]:
    """
    Fetches a user by username from the database.

    Args:
        user_name (str): Username to fetch.
        conn (sqlite3.Connection): SQLite database connection.

    Returns:
        Optional[dict]: User data as a dictionary or None.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_auth WHERE user_name = ?", (user_name,))
        row = cursor.fetchone()
        if row:
            return {
                "user_id": row[0],
                "user_name": row[1],
                "hashed_pass": row[2],
                "full_name": row[3],
                "email": row[4],
                "phone_number": row[5],
                "time_registered": row[6],
                "is_superuser": bool(row[7])  # convert 0/1 to bool
            }
        return None
    except Exception as e:
        logger.error("Failed to fetch user from DB.", exc_info=True)
        raise HTTPException(status_code=500, detail="Database error")


def insert_auth_user(
    user_name: str,
    hashed_pass: str,
    full_name: str,
    email: str,
    phone_number: Optional[str],
    conn: sqlite3.Connection,
    is_superuser: bool = False
) -> None:
    """
    Inserts a new user into the user_auth table.

    Args:
        user_name (str): Username.
        hashed_pass (str): Hashed password.
        full_name (str): Full name of the user.
        email (str): Email address.
        phone_number (Optional[str]): Phone number.
        conn (sqlite3.Connection): SQLite connection.

    Raises:
        HTTPException: If user already exists or database fails.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_auth (
                user_name, hashed_pass, full_name, email,
                phone_number, time_registered, is_superuser
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_name,
            hashed_pass,
            full_name,
            email,
            phone_number,
            datetime.utcnow().isoformat(),
            int(is_superuser)  # convert bool to 0/1
        ))
        conn.commit()
        logger.info("New user registered: %s", user_name)
    except sqlite3.IntegrityError:
        logger.warning("Attempt to register duplicate username: %s", user_name)
        raise HTTPException(status_code=409, detail="Username already exists")
    except Exception as e:
        logger.error("Failed to insert new user.", exc_info=True)
        raise HTTPException(status_code=500, detail="Database insert failed")