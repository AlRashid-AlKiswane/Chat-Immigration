"""

"""

from datetime import datetime, timedelta
from sqlite3 import Connection
import logging

from src.database import (delete_verification_code,
                          fetch_code_verification,
                          insert_code_verification)

def save_verification_code(email: str, code: str, conn: Connection ,expire_minutes=5):
    """
    
    """
    expires = datetime.utcnow() + timedelta(minutes=expire_minutes)
    insert_code_verification(email=email, code=code, expires=expires,
                           conn=conn)

def verify_code(email: str, input_code: str, conn: Connection) -> bool:
    """
    Verifies the email verification code.
    
    Args:
        email (str): User's email address
        input_code (str): Code provided by user
        conn (Connection): Database connection
        
    Returns:
        bool: True if code is valid and not expired, False otherwise
    """
    record = fetch_code_verification(email=email, conn=conn)
    if not record:
        logging.warning("No verification record found for email: %s", email)
        return False

    try:
        # Parse the ISO format datetime string
        expires_dt = datetime.fromisoformat(record["expires"])
    except (ValueError, TypeError) as e:
        logging.error("Invalid datetime format in DB: %s - %s", record["expires"], str(e))
        return False

    # Check if code has expired
    if expires_dt < datetime.utcnow():
        logging.warning("Verification code expired for email: %s", email)
        return False
    
    # Check if code matches
    if record["code"] != input_code:
        logging.warning("Invalid verification code for email: %s", email)
        return False

    # Code is valid - delete it from database to prevent reuse
    delete_verification_code(email=email, conn=conn)
    return True
