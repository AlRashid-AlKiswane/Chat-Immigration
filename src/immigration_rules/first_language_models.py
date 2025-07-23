"""
language_models.py

This module defines the `FirstLanguageFactors` Pydantic model representing
language-related immigration rule points with and without spouse.
It includes functionality to extract, load, and parse these rules from a JSON file.

The module:
- Defines a structured schema for first-language scoring rules.
- Includes logic to extract JSON and load it into the model.
- Handles filesystem setup and robust error logging.
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from pydantic import BaseModel, Field

# Setup base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),  "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set main directory path: %s", e)
    sys.exit(1)

from src.infra import setup_logging
from src.controllers import extract_education_table
logger = setup_logging(name="FIRST_LANGUAGE_MODELS")

class FirstLanguageFactors(BaseModel):
    """
    Pydantic model for first-language CLB level immigration scoring.
    Field names are valid Python identifiers; aliases map to the raw JSON keys.
    """
    clb_4_or_5_with_spouse: int = Field(..., alias="CLB_4_OR_5_WITH_SPOUSE")
    clb_4_or_5_without_spouse: int = Field(..., alias="CLB_4_OR_5_WITHOUT_SPOUSE")
    clb_6_with_spouse: int = Field(..., alias="CLB_6_WITH_SPOUSE")
    clb_6_without_spouse: int = Field(..., alias="CLB_6_WITHOUT_SPOUSE")
    clb_7_with_spouse: int = Field(..., alias="CLB_7_WITH_SPOUSE")
    clb_7_without_spouse: int = Field(..., alias="CLB_7_WITHOUT_SPOUSE")
    clb_8_with_spouse: int = Field(..., alias="CLB_8_WITH_SPOUSE")
    clb_8_without_spouse: int = Field(..., alias="CLB_8_WITHOUT_SPOUSE")
    clb_9_with_spouse: int = Field(..., alias="CLB_9_WITH_SPOUSE")
    clb_9_without_spouse: int = Field(..., alias="CLB_9_WITHOUT_SPOUSE")
    clb_10_or_more_with_spouse: int = Field(..., alias="CLB_10_OR_MORE_WITH_SPOUSE")
    clb_10_or_more_without_spouse: int = Field(..., alias="CLB_10_OR_MORE_WITHOUT_SPOUSE")
    less_than_clb_4_with_spouse: int = Field(..., alias="LESS_THAN_CLB_4_WITH_SPOUSE")
    less_than_clb_4_without_spouse: int = Field(..., alias="LESS_THAN_CLB_4_WITHOUT_SPOUSE")

    class Config:
        validate_by_name = True

def get_first_language_factors(input_json_path: str, extracted_output_path: str) -> FirstLanguageFactors:
    """
    Extracts first language factors from a raw JSON file and loads them into a model.

    Args:
        input_json_path (str): Path to the original raw JSON file.
        extracted_output_path (str): Where to save the extracted flattened JSON.

    Returns:
        FirstLanguageFactors: Pydantic model of language-related scores.

    Raises:
        RuntimeError: On extraction or loading failure.
    """
    try:
        from src.utils import load_json_file
    except ImportError as e:
        logger.error("Import error: %s", e)
        raise RuntimeError("Missing utility functions") from e

    try:
        logger.info("Extracting language rules...")
        extract_education_table(
            input_path=input_json_path,
            output_path=extracted_output_path,
            label_key="Canadian Language Benchmark (CLB) level per ability"
        )
    except Exception as e:
        logger.error("Failed to extract language rules: %s", e)
        raise RuntimeError("Language rules extraction failed") from e

    try:
        logger.info("Loading extracted JSON into model...")
        success, result = load_json_file(file_path=extracted_output_path)
        return FirstLanguageFactors(**result)

    except Exception as e:
        logger.error("Failed to parse JSON: %s", e)
        raise RuntimeError("Language factors model loading failed") from e

def main():
    """
    Run an example of loading first language factors using project settings.
    """
    from src.helpers import get_settings, Settings
    app_settings: Settings = get_settings()

    input_json_path = os.path.join(app_settings.ORGINA_FACTUES_TAPLE, app_settings.FIERST_LANGUAGE_TAPLE_NAME)
    extracted_output_path = os.path.join(app_settings.EXTRACTION_FACTURES_TAPLE, "first_language_factors.json")

    try:
        factors = get_first_language_factors(input_json_path, extracted_output_path)
        logger.info("Language factors loaded successfully.")
        print("CLB 9 WITH spouse:", factors.clb_9_with_spouse)
        print("CLB 10+ WITHOUT spouse:", factors.clb_10_or_more_without_spouse)
    except Exception as e:
        logger.error("Failed to load language data: %s", e)

if __name__ == "__main__":
    main()
