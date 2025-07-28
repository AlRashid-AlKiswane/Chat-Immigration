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

logger = setup_logging(name="LANG_EDU_COMBO_MODEL")

from src.helpers import get_settings, Settings
settings: Settings = get_settings()

input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.LANGUAGE_EDUCATION_TABLE_NAME)
output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "language_education_points.json")


class LanguageEducationCombinationFactors(BaseModel):
    """
    Language and education combination points model.
    Based on CLB 7+ vs CLB 9+ thresholds and education levels.
    """
    high_school_clb7: int = Field(..., alias="SECONDARY_SCHOOL_HIGH_SCHOOL_CREDENTIAL_OR_LESS_CLB7")
    high_school_clb9: int = Field(..., alias="SECONDARY_SCHOOL_HIGH_SCHOOL_CREDENTIAL_OR_LESS_CLB9")

    post_sec_one_plus_clb7: int = Field(..., alias="POST_SECONDARY_PROGRAM_CREDENTIAL_OF_ONE_YEAR_OR_LONGER_CLB7")
    post_sec_one_plus_clb9: int = Field(..., alias="POST_SECONDARY_PROGRAM_CREDENTIAL_OF_ONE_YEAR_OR_LONGER_CLB9")

    two_plus_post_sec_3yr_clb7: int = Field(..., alias="TWO_OR_MORE_POST_SECONDARY_PROGRAM_CREDENTIALS_AND_AT_LEAST_ONE_OF_THESE_CREDENTIALS_WAS_ISSUED_ON_COMPLETION_OF_A_POST_SECONDARY_PROGRAM_OF_THREE_YEARS_OR_LONGER_CLB7")
    two_plus_post_sec_3yr_clb9: int = Field(..., alias="TWO_OR_MORE_POST_SECONDARY_PROGRAM_CREDENTIALS_AND_AT_LEAST_ONE_OF_THESE_CREDENTIALS_WAS_ISSUED_ON_COMPLETION_OF_A_POST_SECONDARY_PROGRAM_OF_THREE_YEARS_OR_LONGER_CLB9")

    masters_or_professional_clb7: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_MASTER_S_LEVEL_OR_AT_THE_LEVEL_OF_AN_ENTRY_TO_PRACTICE_PROFESSIONAL_DEGREE_FOR_AN_OCCUPATION_LISTED_IN_THE_NATIONAL_OCCUPATIONAL_CLASSIFICATION_MATRIX_AT_SKILL_LEVEL_A_FOR_WHICH_LICENSING_BY_A_PROVINCIAL_REGULATORY_BODY_IS_REQUIRED_CLB7")
    masters_or_professional_clb9: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_MASTER_S_LEVEL_OR_AT_THE_LEVEL_OF_AN_ENTRY_TO_PRACTICE_PROFESSIONAL_DEGREE_FOR_AN_OCCUPATION_LISTED_IN_THE_NATIONAL_OCCUPATIONAL_CLASSIFICATION_MATRIX_AT_SKILL_LEVEL_A_FOR_WHICH_LICENSING_BY_A_PROVINCIAL_REGULATORY_BODY_IS_REQUIRED_CLB9")

    doctorate_clb7: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_DOCTORAL_LEVEL_CLB7")
    doctorate_clb9: int = Field(..., alias="A_UNIVERSITY_LEVEL_CREDENTIAL_AT_THE_DOCTORAL_LEVEL_CLB9")

    class Config:
        validate_by_name = True


def get_language_education_points(input_json: str = input_path, extracted_json: str = output_path) -> LanguageEducationCombinationFactors:
    from src.utils import load_json_file
    from src.controllers import extract_language_education_points

    try:
        logger.info("Extracting language + education combination factors...")
        extract_language_education_points(
            input_path=input_json,
            output_path=extracted_json,
            label_key="With good official language proficiency (Canadian Language Benchmark Level [CLB] 7 or higher) and a post-secondary degree"
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise

    try:
        success, data = load_json_file(file_path=extracted_json)
        return LanguageEducationCombinationFactors(**data)  # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise


def calculate_language_education_points(
    education_level: EducationLevel,
    min_clb: int,
    factors: LanguageEducationCombinationFactors
) -> int:
    """
    Calculate language + education combination points based on education level and CLB score.
    """
    logger.info(f"Calculating language+education points for education={education_level}, min CLB={min_clb}")

    # Must be at least CLB 7 to get any points
    if min_clb < 7:
        logger.info("CLB below 7 - no combination points awarded")
        return 0
    
    # Determine which CLB tier applies
    clb_tier = "clb9" if min_clb >= 9 else "clb7"
    
    # Updated mapping aligned with the Skill Transferability table
    education_mapping = {
        # High school or less
        EducationLevel.LESS_THAN_SECONDARY: "high_school",
        EducationLevel.SECONDARY_DIPLOMA: "high_school",
        
        # One/two-year post-secondary AND Bachelor's (3+ years) -> one year+ category
        EducationLevel.ONE_YEAR_POST_SECONDARY: "post_sec_one_plus",
        EducationLevel.TWO_YEAR_POST_SECONDARY: "post_sec_one_plus",
        EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE: "post_sec_one_plus",
        
        # Two or more credentials (with one 3+ years)
        EducationLevel.TWO_OR_MORE_CERTIFICATES: "two_plus_post_sec_3yr",
        
        # Master's and professional degrees
        EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE: "masters_or_professional",
        
        # Doctorate
        EducationLevel.PHD: "doctorate",
    }

    education_category = education_mapping.get(education_level)
    if education_category is None:
        logger.warning(f"Education level '{education_level.value}' not found in mapping.")
        return 0

    # Build the attribute name dynamically
    attr_name = f"{education_category}_{clb_tier}"
    
    try:
        points = getattr(factors, attr_name)
        logger.info(f"Education '{education_level.value}' + CLB {min_clb} => '{attr_name}' => {points} points")
        return points
    except AttributeError:
        logger.error(f"Attribute '{attr_name}' not found in factors model")
        return 0


if __name__ == "__main__":
    try:
        model = get_language_education_points(input_path, output_path)
        print("Loaded language + education combination model:")
        print(f"CLB7 + High School: {model.high_school_clb7}")
        print(f"CLB9 + High School: {model.high_school_clb9}")
        print(f"CLB7 + One Year Post-Sec: {model.post_sec_one_plus_clb7}")
        print(f"CLB9 + One Year Post-Sec: {model.post_sec_one_plus_clb9}")
        print(f"CLB7 + Two+ Credentials: {model.two_plus_post_sec_3yr_clb7}")
        print(f"CLB9 + Two+ Credentials: {model.two_plus_post_sec_3yr_clb9}")
        print(f"CLB7 + Master's: {model.masters_or_professional_clb7}")
        print(f"CLB9 + Master's: {model.masters_or_professional_clb9}")
        print(f"CLB7 + Doctorate: {model.doctorate_clb7}")
        print(f"CLB9 + Doctorate: {model.doctorate_clb9}")
        
        # Test cases
        test_cases = [
            (EducationLevel.ONE_YEAR_POST_SECONDARY, 8),
            (EducationLevel.ONE_YEAR_POST_SECONDARY, 9),
            (EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE, 7),
            (EducationLevel.TWO_OR_MORE_CERTIFICATES, 9),
            (EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE, 9),
            (EducationLevel.SECONDARY_DIPLOMA, 6),  # Should get 0 points
            (EducationLevel.PHD, 9),
        ]
        
        print("\nTest calculations:")
        for education_level, min_clb in test_cases:
            points = calculate_language_education_points(education_level, min_clb, factors=model)
            print(f"{education_level.value} + min CLB {min_clb}: {points} points")

    except Exception as e:
        logger.error("Processing failed: %s", e)
