"""
age_models.py

This module defines the `AgeFactors` Pydantic model representing age-related 
immigration rule points with and without spouse. It includes functionality to extract,
load, and parse these rules from a JSON file.

The module:
- Defines a structured schema for age-based immigration scoring rules.
- Includes asynchronous logic to extract JSON and load it into the model.
- Handles filesystem setup and robust error logging.
"""

import asyncio
import os
from pathlib import Path
import sys
import logging
from pydantic import BaseModel, Field
from typing import Any


# Setup base directory for importing project modules
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    print("MAIN DIR: " + str(MAIN_DIR))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from src.infra import setup_logging

logger = setup_logging(name="AGE_MODELS_FACTORS")

class AgeFactors(BaseModel):
    """
    Pydantic model representing age-related immigration points with and without spouse.
    Field names use valid Python identifiers, with aliases matching raw JSON keys.
    """
    y17_or_less_with_spouse: int = Field(..., alias="17_YEARS_OF_AGE_OR_LESS_WITH_SPOUSE")
    y17_or_less_without_spouse: int = Field(..., alias="17_YEARS_OF_AGE_OR_LESS_WITHOUT_SPOUSE")
    y18_with_spouse: int = Field(..., alias="18_YEARS_OF_AGE_WITH_SPOUSE")
    y18_without_spouse: int = Field(..., alias="18_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y19_with_spouse: int = Field(..., alias="19_YEARS_OF_AGE_WITH_SPOUSE")
    y19_without_spouse: int = Field(..., alias="19_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y20_29_with_spouse: int = Field(..., alias="20_TO_29_YEARS_OF_AGE_WITH_SPOUSE")
    y20_29_without_spouse: int = Field(..., alias="20_TO_29_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y30_with_spouse: int = Field(..., alias="30_YEARS_OF_AGE_WITH_SPOUSE")
    y30_without_spouse: int = Field(..., alias="30_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y31_with_spouse: int = Field(..., alias="31_YEARS_OF_AGE_WITH_SPOUSE")
    y31_without_spouse: int = Field(..., alias="31_YEARS_OF_AGE_WITHOUT_SPOUSE")
    # Continue for other ages...

    class Config:
        validate_by_name = True  # Pydantic v2: replaces allow_population_by_field_name

def get_age_factors(input_json_path: str, extracted_output_path: str) -> AgeFactors:
    """
    Extracts age factors from a raw JSON file and loads them into an AgeFactors model.

    Args:
        input_json_path (str): Path to the original raw JSON file.
        extracted_output_path (str): Path where the processed/extracted JSON will be saved.

    Returns:
        AgeFactors: A populated Pydantic model containing structured age-related factors.

    Raises:
        RuntimeError: If extraction or file loading fails.
    """
    try:
        from src.utils import load_json_file
        from src.controllers import extract_age_json
    except ImportError as e:
        logger.error("Failed to import utilities or controller: %s", e)
        raise RuntimeError("Missing required modules for age factor processing") from e

    try:
        logger.info("Extracting age rules from input JSON...")
        extract_age_json(input_path=input_json_path, output_path=extracted_output_path)
    except Exception as e:
        logger.error("Failed to extract age rules from JSON: %s", e)
        raise RuntimeError("Error extracting age rules") from e

    try:
        logger.info("Loading extracted JSON data into AgeFactors model...")
        success, result = load_json_file(file_path=extracted_output_path)
        age_factors = AgeFactors(**result)
    except Exception as e:
        logger.error("Failed to parse extracted JSON into AgeFactors model: %s", e)
        raise RuntimeError("Error loading age factors from extracted data") from e

    return age_factors

def main():
    """
    Main async function to demonstrate extracting and loading age factors.
    """
    from src.helpers import get_settings, Settings
    app_settings: Settings = get_settings()

    input_json_path = os.path.join(app_settings.ORGINA_FACTUES_TAPLE, app_settings.AGE_TAPLE_NAME)
    extracted_output_path = os.path.join(app_settings.EXTRACTION_FACTURES_TAPLE, "age_factors.json")

    try:
        age_factors = get_age_factors(input_json_path, extracted_output_path)
        logger.info("Successfully loaded age factors.")

        # Example access
        print("Age 30 WITH spouse points:", age_factors.y17_or_less_with_spouse)
        print("Age 30 WITHOUT spouse points:", age_factors.y31_with_spouse)

    except Exception as e:
        logger.error("Failed to process age factors: %s", e)


if __name__ == "__main__":
    main()