"""
Authentication Utilities Module

This module provides core functionality for handling authentication in the FastAPI app,
including password hashing, password verification, JWT token creation, and secret management.

Key Features:
- Secure password hashing using bcrypt via passlib.
- Token generation using JWT with configurable expiration.
- Integrated logging for all actions and errors.
"""

import os
import sqlite3
import sys
import logging
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

# Setup project base path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.critical("Failed to set up project base path.", exc_info=True)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.infra import setup_logging
from src.helpers import get_settings, Settings

# Initialize logging
logger = setup_logging(name="AUTHENTICATION")

# Load application settings
try:
    app_settings: Settings = get_settings()

except Exception as e:
    logger.critical("Failed to load application settings.", exc_info=True)
    sys.exit(1)

# Load sensitive config
SECRET_KEY = app_settings.SECRET_KEY.get_secret_value() if app_settings.SECRET_KEY else None
ALGORITHM = app_settings.ALGORITHM.get_secret_value() if app_settings.ALGORITHM else None

ACCESS_TOKEN_EXPIRE_MINUTES = app_settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Password context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.

    Args:
        password (str): The plain-text password to hash.

    Returns:
        str: The hashed password.

    Raises:
        ValueError: If hashing fails.
    """
    try:
        hashed = pwd_context.hash(password)
        logger.debug("Password hashed successfully.")
        return hashed
    except Exception as e:
        logger.error("Error hashing password.", exc_info=True)
        raise ValueError("Password hashing failed.") from e


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against its hashed counterpart.

    Args:
        plain_password (str): The password provided by the user.
        hashed_password (str): The previously hashed password to compare.

    Returns:
        bool: True if passwords match, False otherwise.

    Raises:
        ValueError: If verification fails due to internal errors.
    """
    try:
        is_valid = pwd_context.verify(plain_password, hashed_password)
        logger.debug("Password verification result: %s", is_valid)
        return is_valid
    except Exception as e:
        logger.error("Error verifying password.", exc_info=True)
        raise ValueError("Password verification failed.") from e


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.

    Args:
        data (dict): Data to encode into the token (e.g., {"sub": username}).
        expires_delta (Optional[timedelta]): Optional token expiry duration.

    Returns:
        str: Encoded JWT token as a string.

    Raises:
        ValueError: If token generation fails.
    """
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info("JWT access token created. Expiry: %s", expire)
        return encoded_jwt
    except Exception as e:
        logger.error("Error creating access token.", exc_info=True)
        raise ValueError("Token creation failed.") from e
