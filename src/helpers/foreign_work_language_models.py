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


class ForeignWorkLanguageCombinationFactors(BaseModel):
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


def get_foreign_work_language_points(input_json: str, extracted_json: str) -> ForeignWorkLanguageCombinationFactors:
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
        return ForeignWorkLanguageCombinationFactors(**data)
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise


if __name__ == "__main__":
    from src.helpers import get_settings, Settings
    settings: Settings = get_settings()

    input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.FOREIGN_WORK_LANGUAGE_TABLE_NAME)
    output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "foreign_work_language_points.json")

    try:
        model = get_foreign_work_language_points(input_path, output_path)
        print("Foreign work experience + language model:")
        print("1 or 2 years & CLB7:", model.one_two_years_clb7)
    except Exception as e:
        logger.error("Processing failed: %s", e)
