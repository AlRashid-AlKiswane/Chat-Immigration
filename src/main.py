
# Set up project base directory
import os
import sys
import logging
from fastapi import FastAPI

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs.logger import setup_logging
from src.helpers import get_settings, Settings
from src.routes import upload_route

# Initialize logger and settings
logger = setup_logging()
app_settings: Settings = get_settings()

app = FastAPI()
app.include_router(upload_route)