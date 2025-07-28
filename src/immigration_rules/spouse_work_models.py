import os
import sys
import logging
from pydantic import BaseModel, Field

# Setup base directory for importing project modules
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from src.infra import setup_logging

logger = setup_logging(name="SPOUSE_WORK_EXPERIENCE_FACTORS")

from src.helpers import get_settings, Settings
app_settings: Settings = get_settings()

input_json_path = os.path.join(app_settings.ORGINA_FACTUES_TAPLE, app_settings.SPOUSE_WORK_EXPERIENCE_TABLE_NAME)
extracted_output_path = os.path.join(app_settings.EXTRACTION_FACTURES_TAPLE, "spouse_work_experience_factors.json")

class SpouseWorkExperienceFactors(BaseModel):
    """
    Pydantic model for spouse's Canadian work experience immigration points.
    Field names follow flat key style and use aliases for deserialization.
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


def get_spouse_work_experience_factors(input_json_path: str =input_json_path, extracted_output_path: str=extracted_output_path) -> SpouseWorkExperienceFactors:
    """
    Extracts and loads spouse Canadian work experience rules into a structured model.

    Args:
        input_json_path (str): Path to the original JSON table file.
        extracted_output_path (str): Path to save the flattened result.

    Returns:
        SpouseWorkExperienceFactors: Parsed model from extracted values.

    Raises:
        RuntimeError: If any step fails.
    """
    try:
        from src.utils import load_json_file
    except ImportError as e:
        logger.error("Import failed: %s", e)
        raise RuntimeError("Utility import failure") from e

    try:
        logger.info("Extracting spouse Canadian work experience rules...")
        from src.controllers import extract_spouse_work_table
        extract_spouse_work_table(
            input_path=input_json_path,
            output_path=extracted_output_path,
            label_key="Spouse's Canadian work experience"
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise RuntimeError("Spouse work experience extraction error") from e

    try:
        logger.info("Loading extracted JSON into model...")
        success, result = load_json_file(file_path=extracted_output_path)
        return SpouseWorkExperienceFactors(**result) # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise RuntimeError("Spouse work experience parsing error") from e
    
def calculate_spouse_work_experience_points(
    years_of_experience: int,
    has_spouse: bool,
    factors: SpouseWorkExperienceFactors
) -> int:
    """
    Calculate CRS points for spouse's Canadian work experience.

    Args:
        years_of_experience (int): Number of years spouse has Canadian work experience.
        has_spouse (bool): Whether spouse is included in the application.
        factors (SpouseWorkExperienceFactors): Loaded scoring factors.

    Returns:
        int: CRS points for spouse work experience.

    Raises:
        ValueError: If input values are invalid.
    """
    logger.info(f"Calculating spouse work experience points for {years_of_experience} years, spouse included: {has_spouse}")

    if not isinstance(years_of_experience, int) or years_of_experience < 0:
        raise ValueError("years_of_experience must be a non-negative integer")

    if not isinstance(has_spouse, bool):
        raise ValueError("has_spouse must be a boolean")

    suffix = "with_spouse" if has_spouse else "without_spouse"

    try:
        if years_of_experience == 0:
            attr_name = f"none_or_less_than_a_year_{suffix}"
        elif years_of_experience == 1:
            attr_name = f"one_year_{suffix}"
        elif years_of_experience == 2:
            attr_name = f"two_years_{suffix}"
        elif years_of_experience == 3:
            attr_name = f"three_years_{suffix}"
        elif years_of_experience == 4:
            attr_name = f"four_years_{suffix}"
        else:  # 5 years or more
            attr_name = f"five_years_or_more_{suffix}"

        points = getattr(factors, attr_name)
        logger.info(f"Spouse work experience points for attribute '{attr_name}': {points}")
        return points

    except AttributeError as e:
        logger.error(f"Attribute '{attr_name}' not found in spouse work experience factors: {e}")
        raise ValueError(f"Invalid spouse work experience attribute: {attr_name}") from e



def main():
    """
    Demonstrates usage of the spouse work experience rule parser.
    """


    try:
        factors = get_spouse_work_experience_factors(input_json_path, extracted_output_path)
        logger.info("Loaded spouse work experience factors.")
        print("5+ years WITH spouse:", factors.five_years_or_more_with_spouse)
        print("None or <1 year WITHOUT spouse:", factors.none_or_less_than_a_year_without_spouse)
        # Example calculation
        example_years = 3
        example_has_spouse = False
        score = calculate_spouse_work_experience_points(example_years, example_has_spouse, factors)
        print(f"Calculated spouse work experience points for {example_years} years (has spouse={example_has_spouse}): {score}")
    except Exception as e:
        logger.error("Processing failed: %s", e)


if __name__ == "__main__":
    main()
