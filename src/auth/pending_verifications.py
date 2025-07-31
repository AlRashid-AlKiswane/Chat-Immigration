


from datetime import datetime, timedelta
from typing import Optional

# Simple in-memory store; replace with DB or Redis in production
pending_verifications = {}

def store_pending_user(email: str, data: dict):
    """
    Stores pending user data in memory.
    
    Args:
        email (str): User's email address
        data (dict): User registration data
    """
    pending_verifications[email] = data


def get_pending_user(email: str) -> Optional[dict]:
    """
    Retrieves pending user data.
    
    Args:
        email (str): User's email address
        
    Returns:
        Optional[dict]: User data or None if not found
    """
    return pending_verifications.get(email)


def remove_pending_user(email: str):
    """
    Removes pending user data after successful registration.
    
    Args:
        email (str): User's email address
    """
    if email in pending_verifications:
        del pending_verifications[email]
