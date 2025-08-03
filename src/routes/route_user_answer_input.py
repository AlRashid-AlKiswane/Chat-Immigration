

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
    HTTP_400_BAD_REQUEST
)
from src.infra.logger import setup_logging
from src.schema import AssessmentResponse, AssessmentAnswers
from src.database import (insert_assessment_data)

from src.helpers import Settings, get_settings
from src.auth import get_current_user
from src import get_db_conn
from src.utils.form_input_preprocessing import transform_assessment_to_crs_params, create_crs_response_data
from src.logic import calculate_comprehensive_crs_score

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
    submission_id = f"sub_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        logger.debug("Attempting to insert assessment data")
        # Convert Pydantic model to dict here
        assessment_dict = assessment_data.dict()

        insert_assessment_data(
            conn=conn, 
            assessment_data=assessment_dict,
            user_name=user['user_name']
        )
        # 2. CALCULATE CRS SCORE
        logger.debug("Step 2: Starting CRS calculation")
        try:
            # Process CRS calculation using external module
            params = transform_assessment_to_crs_params(assessment_data)

            # CALL YOUR CRS CALCULATION FUNCTION HERE
            # Assuming your function is a method of a class, you'll need to instantiate it first
            # If it's a standalone function, you can call it directly like this:
            
            crs_result = calculate_comprehensive_crs_score(
                # Pass all the required parameters from your params dict
                age=params.get('age'), # type: ignore
                marital_status=params.get('marital_status'), # type: ignore
                education_level=params.get('education_level'), # type: ignore
                first_language_test_name=params.get('first_language_test_name'), # type: ignore
                first_language_scores=params.get('first_language_scores'), # type: ignore
                second_language_test_name=params.get('second_language_test_name'),
                second_language_scores=params.get('second_language_scores'),
                canadian_work_experience_years=params.get('canadian_work_experience_years', 0),
                foreign_work_experience_years=params.get('foreign_work_experience_years', 0),
                canadian_citizen_spouse=params.get('canadian_citizen_spouse', False),
                spouse_come_with_you=params.get('spouse_come_with_you', False),
                spouse_education_level=params.get('spouse_education_level'),
                spouse_canadian_work_experience_years=params.get('spouse_canadian_work_experience_years', 0),
                spouse_language_test_name=params.get('spouse_language_test_name'),
                spouse_language_scores=params.get('spouse_language_scores'),
                has_certificate_of_qualification=params.get('has_certificate_of_qualification', False),
                has_sibling_in_canada=params.get('has_sibling_in_canada', False),
                has_provincial_nomination=params.get('has_provincial_nomination', False),
                has_canadian_education=params.get('has_canadian_education', False),
                canadian_education_type=params.get('canadian_education_type', "")
            )
            
            # Create standardized response data
            crs_response_data = create_crs_response_data(
                crs_result=crs_result,
                user_name=user['user_name'],
                include_metadata=True
            )
            
            logger.info(f"✓ CRS calculation completed. Total score: {crs_result.total}")

            # Return success response with CRS results
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "status": "success",
                    "message": "Assessment submitted and CRS calculated successfully",
                    "submission_id": submission_id,
                    "crs_results": crs_response_data
                }
            )
            
        except ValueError as data_error:
            logger.warning(f"CRS calculation failed due to data issues: {str(data_error)}")
            
            # Return partial success - data saved but CRS calculation failed
            return JSONResponse(
                status_code=HTTP_200_OK,
                content={
                    "status": "partial_success",
                    "message": "Assessment submitted successfully, but CRS calculation failed due to incomplete/invalid data",
                    "submission_id": submission_id,
                    "crs_error": {
                        "type": "data_validation_error",
                        "message": str(data_error),
                        "suggestion": "Please review your assessment answers and ensure all required fields are complete"
                    }
                }
            )
        
    except ValueError as validation_error:
        logger.error(f"Assessment validation error: {str(validation_error)}")
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, 
            detail={
                "error": "validation_error",
                "message": f"Invalid data format: {str(validation_error)}",
                "submission_id": submission_id
            }
        )
        
    except Exception as system_error:
        logger.error(f"System error during assessment submission: {str(system_error)}")
        conn.rollback()
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "error": "system_error",
                "message": f"Failed to submit assessment: {str(system_error)}",
                "submission_id": submission_id
            }
        )
