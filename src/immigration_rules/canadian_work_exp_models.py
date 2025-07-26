"""
work_experience_models.py

Defines the `WorkExperienceFactors` model representing immigration points for
Canadian work experience with and without spouse. Includes logic to
extract and load rule data from JSON.

- Structured schema for work experience scoring
- Extraction and model parsing logic
- Logging and filesystem handling
"""

import os
import sys
import logging
from pathlib import Path
from pydantic import BaseModel, Field

# Setup base project path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to resolve project root: %s", e)
    sys.exit(1)

from src.infra import setup_logging
from src.controllers import extract_key_value_table

logger = setup_logging(name="WORK_EXPERIENCE_MODELS")


class WorkExperienceFactors(BaseModel):
    """
    Represents Canadian work experience immigration points with/without spouse.
    """
    none_or_less_than_a_year_with_spouse: int = Field(..., alias="NONE_OR_LESS_THAN_A_YEAR_WITH_SPOUSE")
    none_or_less_than_a_year_without_spouse: int = Field(..., alias="NONE_OR_LESS_THAN_A_YEAR_WITHOUT_SPOUSE")
    one_year_with_spouse: int = Field(..., alias="1_YEAR_WITH_SPOUSE")
    one_year_without_spouse: int = Field(..., alias="1_YEAR_WITHOUT_SPOUSE")
    two_years_with_spouse: int = Field(..., alias="2_YEARS_WITH_SPOUSE")
    two_years_without_spouse: int = Field(..., alias="2_YEARS_WITHOUT_SPOUSE")
    three_years_with_spouse: int = Field(..., alias="3_YEARS_WITH_SPOUSE")
    three_years_without_spouse: int = Field(..., alias="3_YEARS_WITHOUT_SPOUSE")
    four_years_with_spouse: int = Field(..., alias="4_YEARS_WITH_SPOUSE")
    four_years_without_spouse: int = Field(..., alias="4_YEARS_WITHOUT_SPOUSE")
    five_years_or_more_with_spouse: int = Field(..., alias="5_YEARS_OR_MORE_WITH_SPOUSE")
    five_years_or_more_without_spouse: int = Field(..., alias="5_YEARS_OR_MORE_WITHOUT_SPOUSE")

    class Config:
        validate_by_name = True


def get_work_experience_factors(input_json_path: str, extracted_output_path: str) -> WorkExperienceFactors:
    """
    Extracts Canadian work experience rule data and loads it into a model.

    Args:
        input_json_path (str): Path to the original JSON file.
        extracted_output_path (str): Path to save the flattened result.

    Returns:
        WorkExperienceFactors: The populated model.

    Raises:
        RuntimeError: On extraction or parsing error.
    """
    try:
        from src.utils import load_json_file
    except ImportError as e:
        logger.error("Import failed: %s", e)
        raise RuntimeError("Utility import failure") from e

    try:
        logger.info("Extracting work experience rules...")
        extract_key_value_table(
            input_path=input_json_path,
            output_path=extracted_output_path,
            label_key="Canadian work experience"
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise RuntimeError("Work experience extraction error") from e

    try:
        logger.info("Loading extracted JSON into model...")
        success, result = load_json_file(file_path=extracted_output_path)
        return WorkExperienceFactors(**result) # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise RuntimeError("Work experience parsing error") from e
    
def calculate_work_experience_points(
    years_of_experience: int,
    has_spouse: bool,
    factors: WorkExperienceFactors,
) -> int:
    """
    Calculate CRS points for Canadian work experience.

    Args:
        years_of_experience (int): Full years of Canadian work experience.
        has_spouse (bool): Whether the applicant has a spouse.
        factors (WorkExperienceFactors): Points mapping.
        logger: Optional logger instance.

    Returns:
        int: CRS points for work experience.
    """
    # Select suffix based on spouse status
    suffix = "with_spouse" if has_spouse else "without_spouse"

    # Find attribute name for the experience level
    if years_of_experience <= 0:
        attr_name = f"none_or_less_than_a_year_{suffix}"
    elif years_of_experience == 1:
        attr_name = f"one_year_{suffix}"
    elif years_of_experience == 2:
        attr_name = f"two_years_{suffix}"
    elif years_of_experience == 3:
        attr_name = f"three_years_{suffix}"
    elif years_of_experience == 4:
        attr_name = f"four_years_{suffix}"
    else:
        attr_name = f"five_years_or_more_{suffix}"

    # Get points from the model
    points = getattr(factors, attr_name)


    logger.info(
            f"[WORK EXPERIENCE] Years: {years_of_experience}, "
            f"Spouse: {has_spouse}, Attr: {attr_name}, Points: {points}"
        )

    return points


def main():
    """
    Demonstrates usage of the work experience rule parser.
    """
    from src.helpers import get_settings, Settings
    app_settings: Settings = get_settings()

    input_json_path = os.path.join(app_settings.ORGINA_FACTUES_TAPLE, app_settings.WORK_EXPERIENCE_TABLE_NAME)
    extracted_output_path = os.path.join(app_settings.EXTRACTION_FACTURES_TAPLE, "work_experience_factors.json")

    try:
        factors = get_work_experience_factors(input_json_path, extracted_output_path)
        logger.info("Loaded work experience factors.")
        print("5+ years WITHOUT spouse:", factors.five_years_or_more_without_spouse)
        print("1 year WITH spouse:", factors.one_year_with_spouse)
        has_spouse=False
        years_of_experience=3
        points = calculate_work_experience_points(
        years_of_experience=years_of_experience , #user_input
        has_spouse=has_spouse,
        factors=factors,
        )

        print(f"canadian work experience score for {years_of_experience} years, with spouse:  {has_spouse}: {points}")
        has_spouse=True
        points = calculate_work_experience_points(
        years_of_experience=years_of_experience, #user_input
        has_spouse=has_spouse,
        factors=factors,
        )
        print(f"canadian work experience score for {years_of_experience} years, with spouse: {has_spouse}: {points}")  
    except Exception as e:
        logger.error("Processing failed: %s", e)


if __name__ == "__main__":
    main()
