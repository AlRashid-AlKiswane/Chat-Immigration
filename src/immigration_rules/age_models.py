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

import os
import sys
import logging
from pydantic import BaseModel, Field

# Setup base directory for importing project modules
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),  "../.."))
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
    y32_with_spouse: int = Field(..., alias="32_YEARS_OF_AGE_WITH_SPOUSE")
    y32_without_spouse: int = Field(..., alias="32_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y33_with_spouse: int = Field(..., alias="33_YEARS_OF_AGE_WITH_SPOUSE")
    y33_without_spouse: int = Field(..., alias="33_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y34_with_spouse: int = Field(..., alias="34_YEARS_OF_AGE_WITH_SPOUSE")
    y34_without_spouse: int = Field(..., alias="34_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y35_with_spouse: int = Field(..., alias="35_YEARS_OF_AGE_WITH_SPOUSE")
    y35_without_spouse: int = Field(..., alias="35_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y36_with_spouse: int = Field(..., alias="36_YEARS_OF_AGE_WITH_SPOUSE")
    y36_without_spouse: int = Field(..., alias="36_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y37_with_spouse: int = Field(..., alias="37_YEARS_OF_AGE_WITH_SPOUSE")
    y37_without_spouse: int = Field(..., alias="37_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y38_with_spouse: int = Field(..., alias="38_YEARS_OF_AGE_WITH_SPOUSE")
    y38_without_spouse: int = Field(..., alias="38_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y39_with_spouse: int = Field(..., alias="39_YEARS_OF_AGE_WITH_SPOUSE")
    y39_without_spouse: int = Field(..., alias="39_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y40_with_spouse: int = Field(..., alias="40_YEARS_OF_AGE_WITH_SPOUSE")
    y40_without_spouse: int = Field(..., alias="40_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y41_with_spouse: int = Field(..., alias="41_YEARS_OF_AGE_WITH_SPOUSE")
    y41_without_spouse: int = Field(..., alias="41_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y42_with_spouse: int = Field(..., alias="42_YEARS_OF_AGE_WITH_SPOUSE")
    y42_without_spouse: int = Field(..., alias="42_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y43_with_spouse: int = Field(..., alias="43_YEARS_OF_AGE_WITH_SPOUSE")
    y43_without_spouse: int = Field(..., alias="43_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y44_with_spouse: int = Field(..., alias="44_YEARS_OF_AGE_WITH_SPOUSE")
    y44_without_spouse: int = Field(..., alias="44_YEARS_OF_AGE_WITHOUT_SPOUSE")
    y45_or_more_with_spouse: int = Field(..., alias="45_YEARS_OF_AGE_OR_MORE_WITH_SPOUSE")
    y45_or_more_without_spouse: int = Field(..., alias="45_YEARS_OF_AGE_OR_MORE_WITHOUT_SPOUSE")

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
        age_factors = AgeFactors(**result) # type: ignore
    except Exception as e:
        logger.error("Failed to parse extracted JSON into AgeFactors model: %s", e)
        raise RuntimeError("Error loading age factors from extracted data") from e

    return age_factors


def calculate_age_points(age: int, has_spouse: bool, age_factors: AgeFactors) -> int:
    """
    Calculate CRS points based on age and marital status with comprehensive validation.
    
    Args:
        age: Applicant's age (17-100)
        has_spouse: Whether applicant has a spouse
        age_factors: Loaded AgeFactors model
    
    Returns:
        CRS points for age factor
    
    Raises:
        ValueError: For invalid age input
    """
    logger.info(f"Calculating age points for age {age}, spouse: {has_spouse}")

    # Input Validation
    if not isinstance(age, int) or age < 17 or age > 100:
        logger.error(f"Invalid age input: {age}")
        raise ValueError("Age must be an integer between 17 and 100")

    # Determine the attribute suffix based on spouse status
    # This avoids repeating the if/else check in every age condition.
    suffix = "with_spouse" if has_spouse else "without_spouse"

    try:
        # Determine which attribute of age_factors to access based on age
        if age <= 17:
            attr_name = f"y17_or_less_{suffix}"
        elif age == 18:
            attr_name = f"y18_{suffix}"
        elif age == 19:
            attr_name = f"y19_{suffix}"
        elif 20 <= age <= 29: # Assuming JSON data correctly reflects points for 20-29 group
            attr_name = f"y20_29_{suffix}"
        elif age == 30:
            attr_name = f"y30_{suffix}"
        elif age == 31:
            attr_name = f"y31_{suffix}"
        elif age == 32:
            attr_name = f"y32_{suffix}"
        elif age == 33:
            attr_name = f"y33_{suffix}"
        elif age == 34:
            attr_name = f"y34_{suffix}"
        elif age == 35:
            attr_name = f"y35_{suffix}"
        elif age == 36:
            attr_name = f"y36_{suffix}"
        elif age == 37:
            attr_name = f"y37_{suffix}"
        elif age == 38:
            attr_name = f"y38_{suffix}"
        elif age == 39:
            attr_name = f"y39_{suffix}"
        elif age == 40:
            attr_name = f"y40_{suffix}"
        elif age == 41:
            attr_name = f"y41_{suffix}"
        elif age == 42:
            attr_name = f"y42_{suffix}"
        elif age == 43:
            attr_name = f"y43_{suffix}"
        elif age == 44:
            attr_name = f"y44_{suffix}"
        else: # age >= 45
            attr_name = f"y45_or_more_{suffix}"

        # Access the points using getattr
        points = getattr(age_factors, attr_name)
        logger.debug(f"Calculated {points} points for age {age} ({suffix})")
        return points

    except AttributeError as e:
        # This should ideally not happen if the AgeFactors model is correctly populated
        logger.error(f"Age factor attribute not found: {attr_name}. Error: {e}")
        raise RuntimeError(f"Error accessing age factor data for '{attr_name}'") from e
    except Exception as e:
        logger.error(f"Failed to calculate age points: {str(e)}")
        raise RuntimeError("Age points calculation failed") from e

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
        print("Age 30 WITH spouse points:", age_factors.y30_with_spouse)
        print("Age 30 WITHOUT spouse points:", age_factors.y30_without_spouse)

        # Example calculations
        examples = [
            (17, True), (18, False), (25, True), 
            (30, False), (45, True), (50, False)
        ]
        
        for age, has_spouse in examples:
            points = calculate_age_points(age, has_spouse, age_factors)
            status = "with spouse" if has_spouse else "without spouse"
            print(f"Age {age} {status}: {points} points")

    except Exception as e:
        logger.error("Failed to process age factors: %s", e)


if __name__ == "__main__":
    main()
