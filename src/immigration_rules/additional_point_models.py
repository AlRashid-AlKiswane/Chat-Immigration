import os
import sys
import logging
from pydantic import BaseModel, Field

# Setup for importing shared utilities
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except Exception as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from src.infra import setup_logging

logger = setup_logging(name="ADDITIONAL_POINTS_MODEL")

class AdditionalPointsFactors(BaseModel):
    """
    Pydantic model for additional Express Entry points.
    """
    brother_or_sister_living_in_canada_who_is_a_citizen_or_permanent_resident_of_canada: int = Field(..., alias="BROTHER_OR_SISTER_LIVING_IN_CANADA_WHO_IS_A_CITIZEN_OR_PERMANENT_RESIDENT_OF_CANADA")
    scored_nclc_7_or_higher_on_all_four_french_language_skills_and_scored_clb_4_or_lower_in_english_or_didn_t_take_an_english_test: int = Field(..., alias="SCORED_NCLC_7_OR_HIGHER_ON_ALL_FOUR_FRENCH_LANGUAGE_SKILLS_AND_SCORED_CLB_4_OR_LOWER_IN_ENGLISH_OR_DIDN_T_TAKE_AN_ENGLISH_TEST")
    scored_nclc_7_or_higher_on_all_four_french_language_skills_and_scored_clb_5_or_higher_on_all_four_english_skills: int = Field(..., alias="SCORED_NCLC_7_OR_HIGHER_ON_ALL_FOUR_FRENCH_LANGUAGE_SKILLS_AND_SCORED_CLB_5_OR_HIGHER_ON_ALL_FOUR_ENGLISH_SKILLS")
    post_secondary_education_in_canada_credential_of_one_or_two_years: int = Field(..., alias="POST_SECONDARY_EDUCATION_IN_CANADA_CREDENTIAL_OF_ONE_OR_TWO_YEARS")
    post_secondary_education_in_canada_credential_three_years_or_longer: int = Field(..., alias="POST_SECONDARY_EDUCATION_IN_CANADA_CREDENTIAL_THREE_YEARS_OR_LONGER")
    provincial_or_territorial_nomination: int = Field(..., alias="PROVINCIAL_OR_TERRITORIAL_NOMINATION")

    class Config:
        validate_by_name = True

def get_additional_points_factors(input_json: str, extracted_json: str) -> AdditionalPointsFactors:
    from src.utils import load_json_file
    from src.controllers import extract_additional_points

    try:
        logger.info("Extracting additional points factors...")
        extract_additional_points(
            input_path=input_json,
            output_path=extracted_json,
            label_key="Additional points"
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise

    try:
        success, data = load_json_file(file_path=extracted_json)
        return AdditionalPointsFactors(**data)
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise

if __name__ == "__main__":
    from src.helpers import get_settings, Settings
    settings: Settings = get_settings()

    input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.ADDITIONAL_POINTS_TABLE_NAME)
    output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "additional_points_factors.json")

    try:
        model = get_additional_points_factors(input_path, output_path)
        print("Loaded additional points model:")
        print("French + CLB ≥ 5:", model.scored_nclc_7_or_higher_on_all_four_french_language_skills_and_scored_clb_5_or_higher_on_all_four_english_skills)
    except Exception as e:
        logger.error("Processing failed: %s", e)
