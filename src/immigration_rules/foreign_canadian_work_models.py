import os
import sys
import logging
from pydantic import BaseModel, Field

# Setup for main directory and logger
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),  "../.."))
    sys.path.append(MAIN_DIR)
except Exception as e:
    print("Directory setup error:", e)
    sys.exit(1)

from src.infra import setup_logging

logger = setup_logging(name="FOREIGN_CANADIAN_COMBO_MODEL")


class ForeignCanadianWorkFactors(BaseModel):
    """
    Points for foreign work experience + Canadian work experience combination.
    """

    no_experience_canada1: int = Field(..., alias="NO_FOREIGN_WORK_EXPERIENCE_CANADIAN_1YR")
    no_experience_canada2: int = Field(..., alias="NO_FOREIGN_WORK_EXPERIENCE_CANADIAN_2YRS")

    one_two_years_canada1: int = Field(..., alias="ONE_OR_TWO_YEARS_FOREIGN_WORK_CANADIAN_1YR")
    one_two_years_canada2: int = Field(..., alias="ONE_OR_TWO_YEARS_FOREIGN_WORK_CANADIAN_2YRS")

    three_plus_years_canada1: int = Field(..., alias="THREE_YEARS_OR_MORE_FOREIGN_WORK_CANADIAN_1YR")
    three_plus_years_canada2: int = Field(..., alias="THREE_YEARS_OR_MORE_FOREIGN_WORK_CANADIAN_2YRS")

    class Config:
        validate_by_name = True


def get_foreign_canadian_combo_points(input_json: str, extracted_json: str) -> ForeignCanadianWorkFactors:
    from src.utils import load_json_file
    from src.controllers import extract_foreign_canadian_work_points

    try:
        logger.info("Extracting foreign+Canadian work experience points...")
        extract_foreign_canadian_work_points(
            input_path=input_json,
            output_path=extracted_json,
            label_key="Years of experience"
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise

    try:
        success, data = load_json_file(file_path=extracted_json)
        return ForeignCanadianWorkFactors(**data) # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise

def calculate_foreign_canadian_work_points(
    foreign_work_years: int,
    canadian_work_years: int,
    factors: ForeignCanadianWorkFactors
) -> int:
    """
    Calculate CRS points for the combination of foreign work experience and Canadian work experience.

    This function evaluates the points based on these categories:

    - Foreign work experience:
      * No foreign work experience (0 years)
      * One or two years of foreign work experience
      * Three or more years of foreign work experience

    - Canadian work experience:
      * One year (1)
      * Two or more years (2 or more)

    Args:
        foreign_work_years (int): Number of years of foreign work experience (outside Canada).
            Must be a non-negative integer.
        canadian_work_years (int): Number of years of Canadian work experience.
            Must be a non-negative integer.
        factors (ForeignCanadianWorkFactors): An instance of the factors model
            containing CRS points for each combination.

    Returns:
        int: CRS points for foreign + Canadian work experience combination.

    Raises:
        ValueError: If any of the year inputs are negative or invalid.
        AttributeError: If the corresponding attribute is missing in the factors model.
    """
    if foreign_work_years < 0 or canadian_work_years < 0:
        raise ValueError("Work experience years must be non-negative integers")

    # Determine foreign work category key
    if foreign_work_years == 0:
        foreign_key = "no_experience"
    elif 1 <= foreign_work_years <= 2:
        foreign_key = "one_two_years"
    else:  # 3 or more years
        foreign_key = "three_plus_years"

    # Determine Canadian work category suffix key
    if canadian_work_years == 1:
        canada_key = "canada1"
    elif canadian_work_years >= 2:
        canada_key = "canada2"
    else:
        # If 0 years Canadian work experience, no points for combo
        # Could also raise error depending on rules
        return 0

    attr_name = f"{foreign_key}_{canada_key}"

    try:
        points = getattr(factors, attr_name)
    except AttributeError as e:
        raise AttributeError(f"Attribute '{attr_name}' missing in factors model") from e

    return points



if __name__ == "__main__":
    from src.helpers import get_settings, Settings
    settings: Settings = get_settings()

    input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.FOREIGN_CANADIAN_WORK_TABLE_NAME)
    output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "foreign_canadian_work_points.json")

    try:
        model = get_foreign_canadian_combo_points(input_path, output_path)
        print("Foreign + Canadian work combination model:")
        print("1 or 2 years of foreign work experience + (+ 1) year of Canadian work experience points= ", model.one_two_years_canada1)

        points = calculate_foreign_canadian_work_points(
        foreign_work_years=2,
        canadian_work_years=1,
        factors=model
        )
        print(f"CRS points for foreign + Canadian work combo: {points}")
    except Exception as e:
        logger.error("Processing failed: %s", e)
