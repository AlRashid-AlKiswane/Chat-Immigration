"""
Authentication Routes Module

Provides user registration and login endpoints using SQLite and JWT authentication.
Handles password hashing, user existence checks, and secure token generation.

Endpoints:
- POST /api/v1/register: Register a new user
- POST /api/v1/login: Authenticate and receive a JWT token
- POST /api/v1/verify-email: Verify email with code
"""

import os
import sys
import logging
import sqlite3
from datetime import timedelta

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
from src.database import insert_auth_user, fetch_auth_user
from src.helpers import get_settings, Settings
from src.infra import setup_logging
from src.schema import LoginInput, RegisterInput, ResentVerification
from src import get_db_conn
from src.auth import (
    gcode, 
    send_verification_email, 
    save_verification_code,
    verify_code, 
    hash_password, 
    verify_password, 
    create_access_token,
    get_pending_user,
    remove_pending_user,
    store_pending_user
)

# Load settings and logger
app_settings: Settings = get_settings()
logger = setup_logging(name="ROUTE-AUTHENTICATION")

# FastAPI route group
auth_route = APIRouter(
    prefix="/api/v1",
    tags=["AUTHENTICATION"],
    responses={HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


# Updated route handlers (key fixes)
@auth_route.post("/register", status_code=201)
async def register(
    payload: RegisterInput,
    conn: sqlite3.Connection = Depends(get_db_conn)
):
    """
    Registers a new user with hashed password and stores them in SQLite.
    """
    try:
        # Check if username already exists
        existing_user = fetch_auth_user(payload.username, conn)
        if existing_user:
            logger.warning("Username already exists: %s", payload.username)
            raise HTTPException(status_code=400, detail="Username already taken")

        # Check if master key is provided and valid
        is_superuser = False
        if hasattr(payload, 'master_key') and payload.master_key:
            if app_settings.MASTER_KEY and payload.master_key == app_settings.MASTER_KEY.get_secret_value():
                is_superuser = True

        # Generate verification code
        code = gcode()
        
        # Send verification email
        await send_verification_email(email=payload.email, code=code)

        # Save verification code to database
        save_verification_code(email=payload.email, code=code, expire_minutes=5, conn=conn)
        logger.debug("Save Verification code for email: %s******", payload.email.split("@")[0][:2])
        logger.info("Registration initiated for user: %s***", payload.username[:4])

        # Store pending user data (include is_superuser flag)
        user_data = {
            "username": payload.username,
            "password": payload.password,
            "full_name": getattr(payload, 'full_name', None),
            "phone_number": getattr(payload, 'phone_number', None),
            "is_superuser": is_superuser
        }
        store_pending_user(email=payload.email, data=user_data)
        logger.info("Save User Info temporary.")

        return JSONResponse(
            status_code=200,
            content={"status": "pending", "message": "Verification code sent to email"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during registration: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@auth_route.post("/verify-email", status_code=200)
async def verify_email(
    email: str, 
    code: str, 
    conn: sqlite3.Connection = Depends(get_db_conn)
):
    """
    Verify email with code and complete user registration.
    """
    try:
        # Verify the code
        if not verify_code(email=email, input_code=code, conn=conn):
            logger.warning("Invalid verification code for email: %s", email)
            raise HTTPException(status_code=401, detail="Invalid or expired code")

        # Fetch user data from pending storage
        data = get_pending_user(email=email)
        if not data:
            logger.error("No pending user data found for email: %s", email)
            raise HTTPException(status_code=400, detail="No pending registration found")
            
        # Hash the password
        hashed_password = hash_password(data["password"])

        # Insert user into database
        insert_auth_user(
            user_name=data["username"],
            hashed_pass=hashed_password,
            full_name=data.get("full_name"),
            email=email,
            phone_number=data.get("phone_number"),
            is_superuser=data["is_superuser"],
            conn=conn
        )

        # Clean up pending user data
        remove_pending_user(email=email)
    
        logger.info("User registration completed for: %s", data["username"])
        return {"status": "success", "message": "Email verified and user registered"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Email verification failed: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to complete registration")



@auth_route.post("/resend-verification", status_code=200)
async def resend_verification(
    body: ResentVerification, 
    conn: sqlite3.Connection = Depends(get_db_conn)
):
    """
    Resend a verification code to a pending user's email address.
    """
    try:
        # Check if the pending user exists
        data = get_pending_user(email=body.email)
        if not data:
            raise HTTPException(status_code=400, detail="No pending registration found for this email.")

        # Generate a new verification code
        code = gcode()

        # Send email
        await send_verification_email(email=body.email, code=code)

        # Save new verification code to database
        save_verification_code(email=body.email, code=code, expire_minutes=5, conn=conn)

        logger.info("Verification code resent for email: %s", body.email)
        return JSONResponse(status_code=200, content={"message": "Verification code resent successfully."})

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error during resend verification: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to resend verification code.")


@auth_route.post("/login", status_code=200)
async def login(
    payload: LoginInput,
    conn: sqlite3.Connection = Depends(get_db_conn)
):
    """
    Authenticates a user and returns a JWT access token.

    Args:
        payload (LoginInput): Login request body with username and password.
        conn (sqlite3.Connection): Database connection

    Returns:
        dict: JWT access token and status.
    """
    try:
        # Fetch user from database
        user = fetch_auth_user(payload.username, conn)
        if not user:
            logger.warning("Login failed: user not found (%s)", payload.username)
            raise HTTPException(status_code=404, detail="User not found")

        # Verify password
        if not verify_password(payload.password, user["hashed_pass"]):
            logger.warning("Login failed: invalid password for user %s", payload.username)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create access token
        token = create_access_token(
            data={"sub": user["user_name"]},
            expires_delta=timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        logger.info("User logged in successfully: %s", user["user_name"])
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": 'admin' if user.get("is_superuser", False) else 'user'
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected login error: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
