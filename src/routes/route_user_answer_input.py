

from datetime import datetime
import logging
import os
import sys
from typing import Any, Dict, Optional

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
from src.infra.logger import setup_logging
from src.schema import AssessmentResponse, AssessmentAnswers
from src.database import (insert_assessment_data)

from src.helpers import Settings, get_settings
from src.utils import get_current_user
from src import get_db_conn

# Initialize logger and settings
logger = setup_logging(name="ROUTE-SUBMIT-ASSESSMENT")
app_settings: Settings = get_settings()

answers_input_user_route = APIRouter(
    prefix="/api/v1/submit-assessment",
    tags=["Answers Input User"],
    responses={HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

# Helper function to extract language scores
def extract_language_scores(answers_dict: dict, prefix: str) -> Optional[Dict[str, Any]]:
    """Extract language scores for a specific test"""
    scores = {}
    skills = ['listening', 'speaking', 'reading', 'writing']
    
    for skill in skills:
        key = f"{prefix}_{skill}"
        if key in answers_dict:
            scores[skill] = answers_dict[key]
    
    return scores if scores else None

@answers_input_user_route.post("")
async def submit_assessment(
    assessment_data: AssessmentAnswers,
    conn: Connection = Depends(get_db_conn),
    user = Depends(get_current_user)
):
    """Submit Express Entry assessment data and save to database"""
    logger.info(f"Received submission from user: {user['user_name']}")
    logger.debug(f"Submission data: {assessment_data}")
    
    try:
        logger.debug("Attempting to insert assessment data")
        # Convert Pydantic model to dict here
        assessment_dict = assessment_data.dict()
        insert_assessment_data(
            conn=conn, 
            assessment_data=assessment_dict,
            user_name=user['user_name']
        )
        logger.info("Assessment data saved successfully")
        return {"status": "success", "message": "Assessment submitted"}
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(ve)}")
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit assessment: {str(e)}")
