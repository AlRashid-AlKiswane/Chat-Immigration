import os
import sys
import logging
from pydantic import BaseModel, Field
from typing import Any, Optional

# Setup for importing shared utilities
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))  # Added missing parenthesis
    sys.path.append(MAIN_DIR)
except Exception as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from src.infra import setup_logging
from src.enums.value_enums import LanguageTestEnum

logger = setup_logging(name="ADDITIONAL_POINTS_MODEL")

from src.helpers import get_settings, Settings
settings: Settings = get_settings()

input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.ADDITIONAL_POINTS_TABLE_NAME)
output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "additional_points_factors.json")

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

    def __init__(self, **data: Any):
        super().__init__(**data)
        logger.debug(f"AdditionalPointsFactors model initialized with values: {self.dict()}")

def get_additional_points_factors(input_json: str = input_path, extracted_json: str = output_path) -> AdditionalPointsFactors:
    from src.utils import load_json_file
    from src.controllers import extract_additional_points

    try:
        logger.info(f"Starting extraction of additional points factors from {input_json}")
        extract_additional_points(
            input_path=input_json,
            output_path=extracted_json,
            label_key="Additional points"
        )
        logger.info("Extraction completed successfully.")
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise

    try:
        success, data = load_json_file(file_path=extracted_json)
        logger.debug(f"Data loaded from {extracted_json}: {data}")
        return AdditionalPointsFactors(**data)  # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise

def calculate_additional_points(
    points_factors: AdditionalPointsFactors,
    first_test: dict[str, Any],
    second_test: Optional[dict[str, Any]] = None,
    has_sibling_in_canada: bool = False,
    has_provincial_nomination: bool = False,
    canadian_education_years: int = 0
) -> int:
    """
    Calculate the Express Entry additional points based on various criteria.
    """
    logger.info("Calculating additional points...")
    total_points = 0

    # 1. Sibling points
    if has_sibling_in_canada:
        total_points += points_factors.brother_or_sister_living_in_canada_who_is_a_citizen_or_permanent_resident_of_canada
        logger.debug(f"Added sibling points: {total_points}")

    # 2. Language points
    french_tests = {LanguageTestEnum.TEF, LanguageTestEnum.TCF}
    first_is_french = first_test['test_name'] in french_tests
    second_is_french = second_test is not None and second_test['test_name'] in french_tests

    french_clb = (
        first_test['clb_level'] if first_is_french else
        second_test['clb_level'] if second_is_french else 0 # type: ignore
    )
    english_clb = (
        first_test['clb_level'] if not first_is_french else
        second_test['clb_level'] if second_test is not None and not second_is_french else 0
    )

    logger.debug(f"French CLB: {french_clb}, English CLB: {english_clb}")

    if french_clb >= 7:
        if english_clb <= 4:
            total_points += points_factors.scored_nclc_7_or_higher_on_all_four_french_language_skills_and_scored_clb_4_or_lower_in_english_or_didn_t_take_an_english_test
            logger.debug(f"Added French CLB≥7 + English ≤4 points: {total_points}")
        elif english_clb >= 5:
            total_points += points_factors.scored_nclc_7_or_higher_on_all_four_french_language_skills_and_scored_clb_5_or_higher_on_all_four_english_skills
            logger.debug(f"Added French CLB≥7 + English ≥5 points: {total_points}")

    # 3. Canadian education
    if canadian_education_years in {1, 2}:
        total_points += points_factors.post_secondary_education_in_canada_credential_of_one_or_two_years
        logger.debug(f"Added education 1-2 years points: {total_points}")
    elif canadian_education_years >= 3:
        total_points += points_factors.post_secondary_education_in_canada_credential_three_years_or_longer
        logger.debug(f"Added education 3+ years points: {total_points}")

    # 4. Provincial nomination
    if has_provincial_nomination:
        total_points += points_factors.provincial_or_territorial_nomination
        logger.debug(f"Added provincial nomination points: {total_points}")

    logger.info(f"Total additional points: {total_points}")
    return total_points


if __name__ == "__main__":
    try:
        model = get_additional_points_factors(input_path, output_path)
        print("Loaded additional points model:")
        print("French + CLB ≥ 5:", model.scored_nclc_7_or_higher_on_all_four_french_language_skills_and_scored_clb_5_or_higher_on_all_four_english_skills)

        # Example calculations
        test_cases = [
            {
                "name": "French NCLC7 + English CLB4",
                "first_test": {"test_name": LanguageTestEnum.TEF, "clb_level": 7},
                "second_test": {"test_name": LanguageTestEnum.IELTS, "clb_level": 4},
                "sibling": True,
                "education": 2
            },
            {
                "name": "French NCLC8 + No English",
                "first_test": {"test_name": LanguageTestEnum.TCF, "clb_level": 8},
                "sibling": False,
                "education": 0
            },
            {
                "name": "English CLB9 + French NCLC7",
                "first_test": {"test_name": LanguageTestEnum.IELTS, "clb_level": 9},
                "second_test": {"test_name": LanguageTestEnum.TEF, "clb_level": 7},
                "nomination": True
            }
        ]

        for case in test_cases:
            logger.info(f"Running test case: {case['name']}")
            points = calculate_additional_points(
                points_factors=model,
                first_test=case["first_test"],
                second_test=case.get("second_test"),
                has_sibling_in_canada=case.get("sibling", False),
                has_provincial_nomination=case.get("nomination", False),
                canadian_education_years=case.get("education", 0)
            )
            print(f"\nCase: {case['name']}")
            print(f"Total Points: {points}")

    except Exception as e:
        logger.error("Processing failed: %s", e)
