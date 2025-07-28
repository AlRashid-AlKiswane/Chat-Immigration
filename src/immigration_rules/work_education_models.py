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

from src.helpers import get_settings, Settings
settings: Settings = get_settings()

input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.CANADIAN_WORK_EDUCATION_TABLE_NAME)
output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "canadian_work_education_points.json")


class CanadianWorkEducationFactors(BaseModel):
    """
    Canadian work experience and education combination points model.
    Based on official CRS criteria for skill transferability factors.
    """
    # Secondary school (high school) credential or less
    secondary_school_1yr: int = Field(..., alias="SECONDARY_SCHOOL_HIGH_SCHOOL_CREDENTIAL_OR_LESS_1YR")
    secondary_school_2yr: int = Field(..., alias="SECONDARY_SCHOOL_HIGH_SCHOOL_CREDENTIAL_OR_LESS_2YR")

    # Post-secondary program credential of one year or longer (includes Bachelor’s)
    one_year_post_sec_1yr: int = Field(..., alias="POST_SECONDARY_PROGRAM_CREDENTIAL_OF_ONE_YEAR_OR_LONGER_1YR")
    one_year_post_sec_2yr: int = Field(..., alias="POST_SECONDARY_PROGRAM_CREDENTIAL_OF_ONE_YEAR_OR_LONGER_2YR")

    # Two or more post-secondary credentials (3+ year program)
    two_plus_post_sec_3yr_1yr: int = Field(..., alias="TWO_OR_MORE_POST_SECONDARY_PROGRAM_CREDENTIALS_AND_AT_LEAST_ONE_OF_THESE_CREDENTIALS_WAS_ISSUED_ON_COMPLETION_OF_A_POST_SECONDARY_PROGRAM_OF_THREE_YEARS_OR_LONGER_1YR")
    two_plus_post_sec_3yr_2yr: int = Field(..., alias="TWO_OR_MORE_POST_SECONDARY_PROGRAM_CREDENTIALS_AND_AT_LEAST_ONE_OF_THESE_CREDENTIALS_WAS_ISSUED_ON_COMPLETION_OF_A_POST_SECONDARY_PROGRAM_OF_THREE_YEARS_OR_LONGER_2YR")

    # Master's or professional degree
    masters_or_professional_1yr: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_MASTER_S_LEVEL_OR_AT_THE_LEVEL_OF_AN_ENTRY_TO_PRACTICE_PROFESSIONAL_DEGREE_FOR_AN_OCCUPATION_LISTED_IN_THE_NATIONAL_OCCUPATIONAL_CLASSIFICATION_MATRIX_AT_SKILL_LEVEL_A_FOR_WHICH_LICENSING_BY_A_PROVINCIAL_REGULATORY_BODY_IS_REQUIRED_1YR")
    masters_or_professional_2yr: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_MASTER_S_LEVEL_OR_AT_THE_LEVEL_OF_AN_ENTRY_TO_PRACTICE_PROFESSIONAL_DEGREE_FOR_AN_OCCUPATION_LISTED_IN_THE_NATIONAL_OCCUPATIONAL_CLASSIFICATION_MATRIX_AT_SKILL_LEVEL_A_FOR_WHICH_LICENSING_BY_A_PROVINCIAL_REGULATORY_BODY_IS_REQUIRED_2YR")

    # Doctoral level
    doctorate_1yr: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_DOCTORAL_LEVEL_1YR")
    doctorate_2yr: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_DOCTORAL_LEVEL_2YR")

    class Config:
        validate_by_name = True


def get_canadian_work_education_points(input_json: str = input_path, extracted_json: str = output_path) -> CanadianWorkEducationFactors:
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
        return CanadianWorkEducationFactors(**data)  # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise


def calculate_canadian_work_education_points(
    education_level: EducationLevel, 
    canadian_work_years: int, 
    factors: CanadianWorkEducationFactors
) -> int:
    """
    Calculate CRS skill transferability points for Canadian work experience + education combination.
    
    Based on official CRS criteria:
    - Education + 1 year Canadian work experience: up to 25 points
    - Education + 2+ years Canadian work experience: up to 50 points
    """
    logger.info(f"Calculating Canadian work + education points for education={education_level}, work years={canadian_work_years}")

    # No points for less than 1 year of Canadian work experience
    if canadian_work_years < 1:
        logger.info("Less than 1 year Canadian work experience - no points awarded")
        return 0

    # Determine work experience tier: 1 year vs 2+ years
    work_tier = "2yr" if canadian_work_years >= 2 else "1yr"
    
    # ✅ Updated mapping aligned with Skill Transferability table
    education_mapping = {
        EducationLevel.LESS_THAN_SECONDARY: "secondary_school",
        EducationLevel.SECONDARY_DIPLOMA: "secondary_school",
        EducationLevel.ONE_YEAR_POST_SECONDARY: "one_year_post_sec",
        EducationLevel.TWO_YEAR_POST_SECONDARY: "one_year_post_sec",
        EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE: "one_year_post_sec",
        EducationLevel.TWO_OR_MORE_CERTIFICATES: "two_plus_post_sec_3yr",
        EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE: "masters_or_professional",
        EducationLevel.PHD: "doctorate",
    }

    education_category = education_mapping.get(education_level)
    if education_category is None:
        logger.warning(f"Education level '{education_level.value}' not found in mapping")
        return 0

    # Construct attribute name
    attr_name = f"{education_category}_{work_tier}"
    
    try:
        points = getattr(factors, attr_name)
        logger.info(f"Education '{education_level.value}' + {canadian_work_years} year(s) Canadian work => Attribute '{attr_name}' => {points} points")
        return points
    except AttributeError:
        logger.error(f"Attribute '{attr_name}' not found in factors model")
        return 0


if __name__ == "__main__":
    try:
        model = get_canadian_work_education_points(input_path, output_path)
        print("Loaded Canadian work + education combination model:")
        print("1 year + Post-Secondary (1 year+):", model.one_year_post_sec_1yr)
        print("2+ years + Post-Secondary (1 year+):", model.one_year_post_sec_2yr)
        print("1 year + Two or More Credentials (3+ year):", model.two_plus_post_sec_3yr_1yr)
        print("2+ years + Two or More Credentials (3+ year):", model.two_plus_post_sec_3yr_2yr)
        print("1 year + Master's/Professional:", model.masters_or_professional_1yr)
        print("2+ years + Master's/Professional:", model.masters_or_professional_2yr)
        print("1 year + PhD:", model.doctorate_1yr)
        print("2+ years + PhD:", model.doctorate_2yr)

        # Test cases
        test_cases = [
            (EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE, 3),
            (EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE, 1),
            (EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE, 2),
            (EducationLevel.ONE_YEAR_POST_SECONDARY, 1),
            (EducationLevel.SECONDARY_DIPLOMA, 2),
            (EducationLevel.PHD, 3),
        ]

        print("\nTest calculations:")
        for education_level, work_years in test_cases:
            points = calculate_canadian_work_education_points(education_level, work_years, factors=model)
            print(f"Points for {education_level.value} with {work_years} year(s) Canadian work: {points}")

    except Exception as e:
        logger.error("Processing failed: %s", e)
