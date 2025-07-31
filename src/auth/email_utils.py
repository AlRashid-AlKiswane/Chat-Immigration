import os
import aiosmtplib
from email.message import EmailMessage

from src.helpers import Settings, get_settings
SETTINGS: Settings = get_settings()

EAMIL_FROM = SETTINGS.EMAIL_FROM
SMTP_HOST = SETTINGS.SMTP_HOST
SMTP_PORT = SETTINGS.SMTP_PORT
EMAIL_USER = SETTINGS.EMAIL_USER
EMAIL_PASSWORD = SETTINGS.EMAIL_PASSWORD

async def send_verification_email(email: str, code: str):
    """
    
    """
    message = EmailMessage()
    message["From"] = EAMIL_FROM
    message["To"] = email
    message["Subject"] = "Your Verification Code"
    message.set_content(f"Your verification code is: {code}")

    await aiosmtplib.send(
        message,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=EMAIL_USER,
        password=EMAIL_PASSWORD,
        start_tls=True,
    )