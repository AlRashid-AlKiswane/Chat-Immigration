"""
second_language_models.py

Defines the `SecondLanguageFactors` model representing immigration points for
second official language proficiency with and without spouse. Includes logic to
extract and load rule data from JSON.

- Structured schema for second language scoring
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
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),  "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to resolve project root: %s", e)
    sys.exit(1)

from src.infra import setup_logging
from src.controllers import extract_second_language_table

logger = setup_logging(name="SECOND_LANGUAGE_MODELS")

class SecondLanguageFactors(BaseModel):
    """
    Represents second-language CLB immigration points with/without spouse.
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

def get_second_language_factors(input_json_path: str, extracted_output_path: str) -> SecondLanguageFactors:
    """
    Extracts second language rule data and loads it into a model.

    Args:
        input_json_path (str): Path to the original JSON file.
        extracted_output_path (str): Path to save the flattened result.

    Returns:
        SecondLanguageFactors: The populated model.

    Raises:
        RuntimeError: On extraction or parsing error.
    """
    try:
        from src.utils import load_json_file
    except ImportError as e:
        logger.error("Import failed: %s", e)
        raise RuntimeError("Utility import failure") from e

    try:
        logger.info("Extracting second language rules...")
        extract_second_language_table(
            input_path=input_json_path,
            output_path=extracted_output_path,
            label_key="Canadian Language Benchmark (CLB) level per ability"
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise RuntimeError("Second language extraction error") from e

    try:
        logger.info("Loading extracted JSON into model...")
        success, result = load_json_file(file_path=extracted_output_path)
        return SecondLanguageFactors(**result)
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise RuntimeError("Second language parsing error") from e

def main():
    """
    Demonstrates usage of the second-language rule parser.
    """
    from src.helpers import get_settings, Settings
    app_settings: Settings = get_settings()

    input_json_path = os.path.join(app_settings.ORGINA_FACTUES_TAPLE, app_settings.SECOND_LANGUAGE_TAPLE_NAME)
    extracted_output_path = os.path.join(app_settings.EXTRACTION_FACTURES_TAPLE, "second_language_factors.json")

    try:
        factors = get_second_language_factors(input_json_path, extracted_output_path)
        logger.info("Loaded second language factors.")
        print("CLB 9+ WITH spouse:", factors.clb_9_or_more_with_spouse)
        print("CLB 4 or less WITHOUT spouse:", factors.clb_4_or_less_without_spouse)
    except Exception as e:
        logger.error("Processing failed: %s", e)

if __name__ == "__main__":
    main()
