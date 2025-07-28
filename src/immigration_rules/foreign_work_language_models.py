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

logger = setup_logging(name="FOREIGN_WORK_LANG_COMBO_MODEL")

from src.helpers import get_settings, Settings
settings: Settings = get_settings()

input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.FOREIGN_WORK_LANGUAGE_TABLE_NAME)
output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "foreign_work_language_points.json")

class ForeignWorkLanguageFactors(BaseModel):
    """
    Foreign work experience + language level combination points model.
    """

    no_experience_clb7: int = Field(..., alias="NO_FOREIGN_WORK_EXPERIENCE_CLB7")
    no_experience_clb9: int = Field(..., alias="NO_FOREIGN_WORK_EXPERIENCE_CLB9")

    one_two_years_clb7: int = Field(..., alias="ONE_OR_TWO_YEARS_OF_FOREIGN_WORK_EXPERIENCE_CLB7")
    one_two_years_clb9: int = Field(..., alias="ONE_OR_TWO_YEARS_OF_FOREIGN_WORK_EXPERIENCE_CLB9")

    three_plus_years_clb7: int = Field(..., alias="THREE_YEARS_OR_MORE_OF_FOREIGN_WORK_EXPERIENCE_CLB7")
    three_plus_years_clb9: int = Field(..., alias="THREE_YEARS_OR_MORE_OF_FOREIGN_WORK_EXPERIENCE_CLB9")

    class Config:
        validate_by_name = True


def get_foreign_work_language_points(input_json: str =input_path, extracted_json: str =output_path) -> ForeignWorkLanguageFactors:
    from src.utils import load_json_file
    from src.controllers import extract_foreign_work_language_points

    try:
        logger.info("Extracting foreign work experience + language factors...")
        extract_foreign_work_language_points(
            input_path=input_json,
            output_path=extracted_json,
            label_key="Years of experience"
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise

    try:
        success, data = load_json_file(file_path=extracted_json)
        return ForeignWorkLanguageFactors(**data) # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise

def calculate_foreign_work_language_points(
    foreign_work_years: int,
    clb_level: int,
    factors: ForeignWorkLanguageFactors
) -> int:
    """
    Calculate CRS points based on the combination of foreign work experience duration
    and Canadian Language Benchmark (CLB) level using predefined scoring factors.

    The foreign work experience considered must be valid foreign work experience
    (i.e., work experience obtained outside Canada, as recognized by immigration rules).

    The function categorizes years of foreign work experience into three groups:
      - No foreign work experience (0 years)
      - One or two years of foreign work experience
      - Three or more years of foreign work experience

    The CLB level must be either 7 or 9 (or higher), and the scoring differs for CLB 7 and CLB 9.

    Args:
        foreign_work_years (int): Number of years of foreign work experience.
            Should be a non-negative integer.
        clb_level (int): Canadian Language Benchmark level of the applicant's language ability.
            Expected values: typically 7 or 9 (or higher).
        factors (ForeignWorkLanguageCombinationFactors): An instance of the factors model
            containing CRS points for each foreign work experience and CLB level combination.

    Returns:
        int: CRS points for the foreign work experience and language combination.

    Raises:
        ValueError: If foreign_work_years is negative or clb_level is not supported.
        AttributeError: If the corresponding attribute is missing from the factors model.
    """
    if foreign_work_years < 0:
        raise ValueError("foreign_work_years must be a non-negative integer")

    if clb_level < 7:
        raise ValueError("CLB level must be 7 or higher for this calculation")

    # Normalize CLB level to either 7 or 9 (or higher treated as 9)
    if clb_level >= 9:
        clb_key = "clb9"
    else:
        clb_key = "clb7"

    # Determine foreign work experience category
    if foreign_work_years == 0:
        attr_name = f"no_experience_{clb_key}"
    elif 1 <= foreign_work_years <= 2:
        attr_name = f"one_two_years_{clb_key}"
    else:  # 3 or more years
        attr_name = f"three_plus_years_{clb_key}"

    try:
        points = getattr(factors, attr_name)
    except AttributeError as e:
        raise AttributeError(f"Missing attribute '{attr_name}' in factors model") from e

    return points



if __name__ == "__main__":


    try:
        model = get_foreign_work_language_points(input_path, output_path)
        print("Foreign work experience + language model:")
        print("1 or 2 years & CLB7:", model.one_two_years_clb7)
        points = calculate_foreign_work_language_points(
        foreign_work_years=3,
        clb_level=9,
        factors=model
         )
        print(f"CRS Points for foreign work + language: {points}")
    except Exception as e:
        logger.error("Processing failed: %s", e)
