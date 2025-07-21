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
        return ForeignCanadianWorkFactors(**data)
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise


if __name__ == "__main__":
    from src.helpers import get_settings, Settings
    settings: Settings = get_settings()

    input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.FOREIGN_CANADIAN_WORK_TABLE_NAME)
    output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "foreign_canadian_work_points.json")

    try:
        model = get_foreign_canadian_combo_points(input_path, output_path)
        print("Foreign + Canadian work combination model:")
        print("1 or 2 years of foreign work experience + (+ 1) year of Canadian work experience points= ", model.one_two_years_canada1)
    except Exception as e:
        logger.error("Processing failed: %s", e)
