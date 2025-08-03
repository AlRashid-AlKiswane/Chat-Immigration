import os
import sys
import logging

import sqlite3
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# --- Setup project base path ---
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.critical("[Startup Critical] Failed to set project base path.", exc_info=True)
    sys.exit(1)

from src.helpers import Settings, get_settings
from src import get_db_conn
from src.database import fetch_auth_user
app_settings: Settings = get_settings()

# Load sensitive config
SECRET_KEY = app_settings.SECRET_KEY.get_secret_value() if app_settings.SECRET_KEY else None
ALGORITHM = app_settings.ALGORITHM.get_secret_value() if app_settings.ALGORITHM else None
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

def get_current_user(
    conn: sqlite3.Connection = Depends(get_db_conn),
    token: str = Depends(oauth2_scheme),
) -> dict:
    """
    Extracts and verifies user from JWT token.

    Returns:
        dict: Full user dict from the database.
    """
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception

        user = fetch_auth_user(username, conn)
        if not user:
            raise credentials_exception

        image_url = f"/media/profiles/{user["user_name"]}.jpg"
        user["image_filename"] = image_url if image_url else None

        return user

    except JWTError:
        raise credentials_exception

def get_current_superuser(user: dict = Depends(get_current_user)) -> dict:
    if not user.get("is_superuser", False):
        raise HTTPException(status_code=403, detail="You do not have sufficient privileges.")
    return user
