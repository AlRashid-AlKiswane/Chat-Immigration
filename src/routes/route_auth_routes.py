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

from fastapi import APIRouter, HTTPException, Depends
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
from src.database.table_db.db_user import insert_auth_user
from src.helpers import get_settings, Settings, hash_password, verify_password, create_access_token
from src.infra import setup_logging
from src.database import fetch_auth_user
from src.schema import LoginInput, RegisterInput
from src import get_db_conn

# Load settings and logger
app_settings: Settings = get_settings()
logger = setup_logging(name="ROUTE-AUTHENTICATION")


# FastAPI route group
auth_route = APIRouter(
    prefix="/api/v1",
    tags=["AUTHENTICATION"],
    responses={HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@auth_route.post("/register", status_code=201)
async def register(
    payload: RegisterInput,
    conn: sqlite3.Connection = Depends(get_db_conn)
):
    """
    Registers a new user with hashed password and stores them in SQLite.

    Args:
        username (str): Username.
        password (str): Plain-text password.
        email (str): Email address.
        phone_number (Optional[str]): Phone number.
        full_name (Optional[str]): Full name.

    Returns:
        JSONResponse: Registration status.
    """
    try:
        is_superuser = (
            payload.master_key == app_settings.MASTER_KEY.get_secret_value() 
            if app_settings.MASTER_KEY else False
        )
    except Exception as e:
        logger.critical("Can't Extraction [MASTERKEY]: %s", e)
    try:
        if fetch_auth_user(payload.username, conn=conn):
            logger.warning("Username already exists: %s", payload.username)
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed = hash_password(payload.password)

        insert_auth_user(
            user_name=payload.username,
            hashed_pass=hashed,
            full_name=payload.full_name,
            email=payload.email,
            phone_number=payload.phone_number,
            is_superuser=is_superuser,
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
async def login(payload: LoginInput,
                conn: sqlite3.Connection = Depends(get_db_conn)):
    """
    Authenticates a user and returns a JWT access token.

    Args:
        payload (LoginInput): Login request body with username and password.

    Returns:
        dict: JWT access token and status.
    """
    try:
        user = fetch_auth_user(payload.username, conn)
        if not user:
            logger.warning("Login failed: user not found (%s)", payload.username)
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(payload.password, user["hashed_pass"]):
            logger.warning("Login failed: invalid password for user %s", payload.username)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token(
            data={"sub": user["user_name"]},
            expires_delta=timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        logger.info("User logged in: %s", user["user_name"])
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": 'admin' if user["is_superuser"] else 'user'
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Unexpected login error.", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
