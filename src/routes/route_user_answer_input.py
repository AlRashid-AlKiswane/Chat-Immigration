

import logging
import os
import sys

# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from sqlite3 import Connection  # Ensure Pylint recognizes it as a valid type
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from chromadb import Client
from src.infra.logger import setup_logging
from src import get_db_conn, get_vdb_client, get_embedd
from src.database import fetch_all_rows, insert_documents
from src.embeddings import BaseEmbeddings

# Initialize logger and settings
logger = setup_logging(name="ROUTE-CHUNKS-EMBEDDING")

answers_input_user_route = APIRouter(
    prefix="/api/v1/answers_input_user",
    tags=["Answers Input User"],
    responses={HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@answers_input_user_route.post()




