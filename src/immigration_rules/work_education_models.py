import os
import sys
import logging
from pydantic import BaseModel, Field

# Setup for importing shared utilities
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),  "../.."))
    sys.path.append(MAIN_DIR)
except Exception as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from src.infra import setup_logging

logger = setup_logging(name="CANADIAN_WORK_EDU_MODEL")

class CanadianWorkEducationFactors(BaseModel):
    """
    Canadian work experience and education combination points model.
    """

    secondary_school_1YR: int = Field(..., alias="SECONDARY_SCHOOL_HIGH_SCHOOL_CREDENTIAL_OR_LESS_1YR")
    secondary_school_2YR: int = Field(..., alias="SECONDARY_SCHOOL_HIGH_SCHOOL_CREDENTIAL_OR_LESS_2YR")

    one_year_post_sec_1YR: int = Field(..., alias="POST_SECONDARY_PROGRAM_CREDENTIAL_OF_ONE_YEAR_OR_LONGER_1YR")
    one_year_post_sec_2YR: int = Field(..., alias="POST_SECONDARY_PROGRAM_CREDENTIAL_OF_ONE_YEAR_OR_LONGER_2YR")

    two_or_more_post_sec_1YR: int = Field(..., alias="TWO_OR_MORE_POST_SECONDARY_PROGRAM_CREDENTIALS_AND_AT_LEAST_ONE_OF_THESE_CREDENTIALS_WAS_ISSUED_ON_COMPLETION_OF_A_POST_SECONDARY_PROGRAM_OF_THREE_YEARS_OR_LONGER_1YR")
    two_or_more_post_sec_2YR: int = Field(..., alias="TWO_OR_MORE_POST_SECONDARY_PROGRAM_CREDENTIALS_AND_AT_LEAST_ONE_OF_THESE_CREDENTIALS_WAS_ISSUED_ON_COMPLETION_OF_A_POST_SECONDARY_PROGRAM_OF_THREE_YEARS_OR_LONGER_2YR")

    masters_or_prof_1YR: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_MASTER_S_LEVEL_OR_AT_THE_LEVEL_OF_AN_ENTRY_TO_PRACTICE_PROFESSIONAL_DEGREE_FOR_AN_OCCUPATION_LISTED_IN_THE_NATIONAL_OCCUPATIONAL_CLASSIFICATION_MATRIX_AT_SKILL_LEVEL_A_FOR_WHICH_LICENSING_BY_A_PROVINCIAL_REGULATORY_BODY_IS_REQUIRED_1YR")
    masters_or_prof_2YR: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_MASTER_S_LEVEL_OR_AT_THE_LEVEL_OF_AN_ENTRY_TO_PRACTICE_PROFESSIONAL_DEGREE_FOR_AN_OCCUPATION_LISTED_IN_THE_NATIONAL_OCCUPATIONAL_CLASSIFICATION_MATRIX_AT_SKILL_LEVEL_A_FOR_WHICH_LICENSING_BY_A_PROVINCIAL_REGULATORY_BODY_IS_REQUIRED_2YR")

    doctorate_1YR: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_DOCTORAL_LEVEL_1YR")
    doctorate_2YR: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_DOCTORAL_LEVEL_2YR")

    class Config:
        validate_by_name = True

def get_canadian_work_education_points(input_json: str, extracted_json: str) -> CanadianWorkEducationFactors:
    from src.utils import load_json_file
    from src.controllers import extract_canadian_work_edu_points

    try:
        logger.info("Extracting Canadian work + education combination factors...")
        extract_canadian_work_edu_points(
            input_path=input_json,
            output_path=extracted_json,
            label_key="With Canadian work experience and a post-secondary degree"
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise

    try:
        success, data = load_json_file(file_path=extracted_json)
        return CanadianWorkEducationFactors(**data)
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise

if __name__ == "__main__":
    from src.helpers import get_settings, Settings
    settings: Settings = get_settings()

    input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.CANADIAN_WORK_EDUCATION_TABLE_NAME)
    output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "canadian_work_education_points.json")

    try:
        model = get_canadian_work_education_points(input_path, output_path)
        print("Loaded Canadian work + education model:")
        print("2YR + Master's:", model.masters_or_prof_2YR)
    except Exception as e:
        logger.error("Processing failed: %s", e)
