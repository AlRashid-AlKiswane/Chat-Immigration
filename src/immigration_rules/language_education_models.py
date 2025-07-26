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

class LanguageEducationCombinationFactors(BaseModel):
    """
    Language and education combination points model.
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

def get_language_education_points(input_json: str, extracted_json: str) -> LanguageEducationCombinationFactors:
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
        return LanguageEducationCombinationFactors(**data) # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise



def calculate_language_education_points(
    education_level: EducationLevel,
    min_clb: int,
    factors: LanguageEducationCombinationFactors
) -> int:
    logger.info(f"Calculating language+education points for education={education_level}, min CLB={min_clb}")

    clb_threshold = 9 if min_clb >= 9 else 7

    # Map enum to factor attribute names
    mapping = {
        EducationLevel.SECONDARY_DIPLOMA: f"high_school_clb{clb_threshold}",
        EducationLevel.ONE_YEAR_POST_SECONDARY: f"post_sec_one_plus_clb{clb_threshold}",
        EducationLevel.TWO_OR_MORE_CERTIFICATES: f"two_plus_post_sec_3yr_clb{clb_threshold}",
        EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE: f"masters_or_professional_clb{clb_threshold}",
        EducationLevel.PHD: f"doctorate_clb{clb_threshold}",
    }

    attr_name = mapping.get(education_level, None)
    if attr_name is None:
        logger.warning(f"Education level '{education_level.value}' not mapped for points calculation.")
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

    input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.LANGUAGE_EDUCATION_TABLE_NAME)
    output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "language_education_points.json")

    try:
        model = get_language_education_points(input_path, output_path)
        print("Loaded language + education combination model:")
        print("CLB9 + Doctorate:", model.doctorate_clb9)
        education_level= EducationLevel.ONE_YEAR_POST_SECONDARY
        min_clb=8

        points = calculate_language_education_points(education_level, min_clb, factors=model)
        print(f"Points for {education_level.value} with min CLB {min_clb}: {points}")

    except Exception as e:
        logger.error("Processing failed: %s", e)
