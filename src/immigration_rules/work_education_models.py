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
from src.enums.value_enums import EducationLevel

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
        return CanadianWorkEducationFactors(**data) # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise

def calculate_canadian_work_education_points(education_level: EducationLevel, canadian_work_years: int, factors: CanadianWorkEducationFactors) -> int:
    """
    Calculate CRS points based on the combination of the applicant's education level 
    and Canadian work experience duration using predefined scoring factors.

    The Canadian work experience considered must be **valid Canadian work experience** 
    (i.e., work performed in Canada, meeting immigration program requirements).

    The function differentiates scoring based on whether the Canadian work experience 
    is at least 2 years or less, applying the corresponding points from the factors model.

    Args:
        education_level (EducationLevel): The highest education credential of the applicant.
            Must be one of the predefined EducationLevel enum values.
        canadian_work_years (int): Number of years of Canadian work experience.
            Only Canadian work experience counts towards these points.
        factors (CanadianWorkEducationFactors): An instance of the factors model containing
            the CRS points associated with each education and Canadian work experience combination.

    Returns:
        int: CRS points corresponding to the combined education level and Canadian work experience.

    Raises:
        AttributeError: If the corresponding attribute for the education and work year 
            combination is not found in the factors model.
    """
    logger.info(f"Calculating Canadian work + education points for education={education_level}, work years={canadian_work_years}")

    # Choose 1YR or 2YR bucket (2YR if years >= 2 else 1YR)
    year_suffix = "2YR" if canadian_work_years >= 2 else "1YR"

    mapping = {
        EducationLevel.SECONDARY_DIPLOMA: f"secondary_school_{year_suffix}",
        EducationLevel.ONE_YEAR_POST_SECONDARY: f"one_year_post_sec_{year_suffix}",
        EducationLevel.TWO_OR_MORE_CERTIFICATES: f"two_or_more_post_sec_{year_suffix}",
        EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE: f"masters_or_prof_{year_suffix}",
        EducationLevel.PHD: f"doctorate_{year_suffix.lower()}",
    }

    attr_name = mapping.get(education_level, None)
    if attr_name is None:
        logger.warning(f"Education level '{education_level.value}' not mapped.")
        return 0

    try:
        points = getattr(factors, attr_name)
        logger.info(f"Attribute '{attr_name}' => {points} points")
        return points
    except AttributeError:
        logger.error(f"Attribute '{attr_name}' not found in factors")
        return 0

if __name__ == "__main__":
    from src.helpers import get_settings, Settings
    settings: Settings = get_settings()

    input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.CANADIAN_WORK_EDUCATION_TABLE_NAME)
    output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "canadian_work_education_points.json")

    try:
        model = get_canadian_work_education_points(input_path, output_path)
        print("Loaded Canadian work + education model:")
        print("2YR + Master's:", model.masters_or_prof_2YR)

        # Test call
        education_level = EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE
        canadian_work_years = 2

        points = calculate_canadian_work_education_points(education_level, canadian_work_years, factors=model)
        print(f"Points for {education_level.value} with {canadian_work_years} year(s) Canadian work experience: {points}")

    except Exception as e:
        logger.error("Processing failed: %s", e)
