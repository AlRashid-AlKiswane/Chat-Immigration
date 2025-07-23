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


def get_spouse_work_experience_factors(input_json_path: str, extracted_output_path: str) -> SpouseWorkExperienceFactors:
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
        return SpouseWorkExperienceFactors(**result)
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise RuntimeError("Spouse work experience parsing error") from e


def main():
    """
    Demonstrates usage of the spouse work experience rule parser.
    """
    from src.helpers import get_settings, Settings
    app_settings: Settings = get_settings()

    input_json_path = os.path.join(app_settings.ORGINA_FACTUES_TAPLE, app_settings.SPOUSE_WORK_EXPERIENCE_TABLE_NAME)
    extracted_output_path = os.path.join(app_settings.EXTRACTION_FACTURES_TAPLE, "spouse_work_experience_factors.json")

    try:
        factors = get_spouse_work_experience_factors(input_json_path, extracted_output_path)
        logger.info("Loaded spouse work experience factors.")
        print("5+ years WITH spouse:", factors.five_years_or_more_with_spouse)
        print("None or <1 year WITHOUT spouse:", factors.none_or_less_than_a_year_without_spouse)
    except Exception as e:
        logger.error("Processing failed: %s", e)


if __name__ == "__main__":
    main()
