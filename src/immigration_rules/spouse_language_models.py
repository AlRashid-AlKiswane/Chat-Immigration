import os
from pathlib import Path
import sys
import logging
from pydantic import BaseModel, Field
from typing import Any



# Setup base directory for importing project modules
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),  "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from src.infra import setup_logging

logger = setup_logging(name="SPOUSE_LANGUAGE_MODELS_FACTORS")

class SpouseLanguageFactors(BaseModel):
    """
    Pydantic model for language benchmark level immigration scoring.
    Field names are valid Python identifiers; aliases map to the raw JSON keys.
    """
    clb_4_or_less_with_spouse: int = Field(..., alias="CLB_4_OR_LESS_WITH_SPOUSE")
    clb_4_or_less_without_spouse: int = Field(..., alias="CLB_4_OR_LESS_WITHOUT_SPOUSE")
    clb_5_or_6_with_spouse: int = Field(..., alias="CLB_5_OR_6_WITH_SPOUSE")
    clb_5_or_6_without_spouse: int = Field(..., alias="CLB_5_OR_6_WITHOUT_SPOUSE")
    clb_7_or_8_with_spouse: int = Field(..., alias="CLB_7_OR_8_WITH_SPOUSE")
    clb_7_or_8_without_spouse: int = Field(..., alias="CLB_7_OR_8_WITHOUT_SPOUSE")
    clb_9_or_more_with_spouse: int = Field(..., alias="CLB_9_OR_MORE_WITH_SPOUSE")
    clb_9_or_more_without_spouse: int = Field(..., alias="CLB_9_OR_MORE_WITHOUT_SPOUSE")

    class Config:
        validate_by_name = True

def get_spouse_language_factors(input_json_path: str, extracted_output_path: str) -> SpouseLanguageFactors:
    """
    Extracts spouse language rule data and loads it into a model.

    Args:
        input_json_path (str): Path to the original JSON file.
        extracted_output_path (str): Path to save the flattened result.

    Returns:
        SpouseLanguageFactors: The populated model.

    Raises:
        RuntimeError: On extraction or parsing error.
    """
    try:
        from src.utils import load_json_file
    except ImportError as e:
        logger.error("Import failed: %s", e)
        raise RuntimeError("Utility import failure") from e

    try:
        logger.info("Extracting spouse language rules...")
        from src.controllers import extract_spouse_language_table
        extract_spouse_language_table(
            input_path=input_json_path,
            output_path=extracted_output_path,
            label_key="Canadian Language Benchmark (CLB) level per ability (reading, writing, speaking and listening)"
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise RuntimeError("Spouse language extraction error") from e

    try:
        logger.info("Loading extracted JSON into model...")
        success, result = load_json_file(file_path=extracted_output_path)
        return SpouseLanguageFactors(**result)
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise RuntimeError("Spouse language parsing error") from e


def main():
    """
    Demonstrates usage of the spouse language rule parser.
    """
    from src.helpers import get_settings, Settings
    app_settings: Settings = get_settings()

    input_json_path = os.path.join(app_settings.ORGINA_FACTUES_TAPLE, app_settings.SPOUSE_LANGUAGE_TABLE_NAME)
    extracted_output_path = os.path.join(app_settings.EXTRACTION_FACTURES_TAPLE, "spouse_language_factors.json")

    try:
        factors = get_spouse_language_factors(input_json_path, extracted_output_path)
        logger.info("Loaded spouse language factors.")
        print("CLB 9+ WITH spouse:", factors.clb_9_or_more_with_spouse)
        print("CLB 5-6 WITHOUT spouse:", factors.clb_5_or_6_without_spouse)
    except Exception as e:
        logger.error("Processing failed: %s", e)


if __name__ == "__main__":
    main()
