"""
Authentication Routes Module

Provides user registration and login endpoints using SQLite and JWT authentication.
Handles password hashing, user existence checks, and secure token generation.

Endpoints:
- POST /api/v1/register: Register a new user
- POST /api/v1/login: Authenticate and receive a JWT token
"""

import os
import sys
import logging
import sqlite3
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Setup project path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.critical("Failed to set up project base path: %s", e)
    sys.exit(1)

# Local imports
from src.helpers import get_settings, Settings, hash_password, verify_password, create_access_token
from src.infra import setup_logging
from src.database import get_sqlite_engine
from src.schema import LoginInput

# Load settings and logger
app_settings: Settings = get_settings()
AUTH_DB = app_settings.AUTH_DB
logger = setup_logging(name="ROUTE-AUTHENTICATION")

# Database connection
conn = get_sqlite_engine(db_conn=AUTH_DB)


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
                time_registered TEXT NOT NULL
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
    conn: sqlite3.Connection
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
                user_name, hashed_pass, full_name, email, phone_number, time_registered
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_name,
            hashed_pass,
            full_name,
            email,
            phone_number,
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        logger.info("New user registered: %s", user_name)
    except sqlite3.IntegrityError:
        logger.warning("Attempt to register duplicate username: %s", user_name)
        raise HTTPException(status_code=409, detail="Username already exists")
    except Exception as e:
        logger.error("Failed to insert new user.", exc_info=True)
        raise HTTPException(status_code=500, detail="Database insert failed")


# Ensure the auth table exists
create_auth_user_table(conn)

# FastAPI route group
auth_route = APIRouter(
    prefix="/api/v1",
    tags=["AUTHENTICATION"],
    responses={HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@auth_route.post("/register", status_code=201)
async def register(
    user_name: str,
    password: str,
    email: str,
    phone_number: Optional[str] = None,
    full_name: Optional[str] = ""
):
    """
    Registers a new user with hashed password and stores them in SQLite.

    Args:
        user_name (str): Username.
        password (str): Plain-text password.
        email (str): Email address.
        phone_number (Optional[str]): Phone number.
        full_name (Optional[str]): Full name.

    Returns:
        JSONResponse: Registration status.
    """
    try:
        if fetch_auth_user(user_name, conn=conn):
            logger.warning("Username already exists: %s", user_name)
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed = hash_password(password)

        insert_auth_user(
            user_name=user_name,
            hashed_pass=hashed,
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            conn=conn
        )

        return JSONResponse(
            status_code=201,
            content={"status": "success", "message": "User registered successfully"}
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.exception("Unexpected error during registration.")
        raise HTTPException(status_code=500, detail="Internal server error")


@auth_route.post("/login", status_code=200)
async def login(payload: LoginInput):
    """
    Authenticates a user and returns a JWT access token.

    Args:
        payload (LoginInput): Login request body with username and password.

    Returns:
        dict: JWT access token and status.
    """
    try:
        user = fetch_auth_user(payload.user_name, conn)
        if not user:
            logger.warning("Login failed: user not found (%s)", payload.user_name)
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(payload.password, user["hashed_pass"]):
            logger.warning("Login failed: invalid password for user %s", payload.user_name)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token(
            data={"sub": user["user_name"]},
            expires_delta=timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        logger.info("User logged in: %s", user["user_name"])
        return {
            "status": "success",
            "access_token": token,
            "token_type": "bearer"
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Unexpected login error.", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
