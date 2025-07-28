import sqlite3
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

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

        return user

    except JWTError:
        raise credentials_exception

def get_current_superuser(user: dict = Depends(get_current_user)) -> dict:
    if not user.get("is_superuser", False):
        raise HTTPException(status_code=403, detail="You do not have sufficient privileges.")
    return user
