"""
education_models.py

This module defines the `EducationFactors` Pydantic model representing education-related 
immigration rule points with and without spouse. It includes functionality to extract,
load, and parse these rules from a JSON file.

The module:
- Defines a structured schema for education-based immigration scoring rules.
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
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    print("MAIN DIR: " + str(MAIN_DIR))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from src.infra import setup_logging
from src.controllers import extract_education_table

logger = setup_logging(name="EDUCATION_MODELS_FACTORS")

class EducationFactors(BaseModel):
    """
    Pydantic model representing education-related immigration points with and without spouse.
    Field names use valid Python identifiers, with aliases matching raw JSON keys.
    """
    less_than_secondary_with_spouse: int = Field(..., alias="LESS_THAN_SECONDARY_SCHOOL_HIGH_SCHOOL_WITH_SPOUSE")
    less_than_secondary_without_spouse: int = Field(..., alias="LESS_THAN_SECONDARY_SCHOOL_HIGH_SCHOOL_WITHOUT_SPOUSE")
    secondary_diploma_with_spouse: int = Field(..., alias="SECONDARY_DIPLOMA_HIGH_SCHOOL_GRADUATION_WITH_SPOUSE")
    secondary_diploma_without_spouse: int = Field(..., alias="SECONDARY_DIPLOMA_HIGH_SCHOOL_GRADUATION_WITHOUT_SPOUSE")
    one_year_program_with_spouse: int = Field(..., alias="ONE_YEAR_DEGREE_DIPLOMA_OR_CERTIFICATE_FROM_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITH_SPOUSE")
    one_year_program_without_spouse: int = Field(..., alias="ONE_YEAR_DEGREE_DIPLOMA_OR_CERTIFICATE_FROM_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITHOUT_SPOUSE")
    two_year_program_with_spouse: int = Field(..., alias="TWO_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITH_SPOUSE")
    two_year_program_without_spouse: int = Field(..., alias="TWO_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITHOUT_SPOUSE")
    bachelors_with_spouse: int = Field(..., alias="BACHELOR_S_DEGREE_OR_A_THREE_OR_MORE_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITH_SPOUSE")
    bachelors_without_spouse: int = Field(..., alias="BACHELOR_S_DEGREE_OR_A_THREE_OR_MORE_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITHOUT_SPOUSE")
    two_or_more_certificates_with_spouse: int = Field(..., alias="TWO_OR_MORE_CERTIFICATES_DIPLOMAS_OR_DEGREES_ONE_MUST_BE_FOR_A_PROGRAM_OF_THREE_OR_MORE_YEARS_WITH_SPOUSE")
    two_or_more_certificates_without_spouse: int = Field(..., alias="TWO_OR_MORE_CERTIFICATES_DIPLOMAS_OR_DEGREES_ONE_MUST_BE_FOR_A_PROGRAM_OF_THREE_OR_MORE_YEARS_WITHOUT_SPOUSE")
    masters_or_professional_with_spouse: int = Field(..., alias="MASTER_S_DEGREE_OR_PROFESSIONAL_DEGREE_NEEDED_TO_PRACTICE_IN_A_LICENSED_PROFESSION_FOR_PROFESSIONAL_DEGREE_THE_DEGREE_PROGRAM_MUST_HAVE_BEEN_IN_MEDICINE_VETERINARY_MEDICINE_DENTISTRY_OPTOMETRY_LAW_CHIROPRACTIC_MEDICINE_OR_PHARMACY_WITH_SPOUSE")
    masters_or_professional_without_spouse: int = Field(..., alias="MASTER_S_DEGREE_OR_PROFESSIONAL_DEGREE_NEEDED_TO_PRACTICE_IN_A_LICENSED_PROFESSION_FOR_PROFESSIONAL_DEGREE_THE_DEGREE_PROGRAM_MUST_HAVE_BEEN_IN_MEDICINE_VETERINARY_MEDICINE_DENTISTRY_OPTOMETRY_LAW_CHIROPRACTIC_MEDICINE_OR_PHARMACY_WITHOUT_SPOUSE")
    phd_with_spouse: int = Field(..., alias="DOCTORAL_LEVEL_UNIVERSITY_DEGREE_PH_D_WITH_SPOUSE")
    phd_without_spouse: int = Field(..., alias="DOCTORAL_LEVEL_UNIVERSITY_DEGREE_PH_D_WITHOUT_SPOUSE")

    class Config:
        validate_by_name = True

def get_education_factors(input_json_path: str, extracted_output_path: str) -> EducationFactors:
    """
    Extracts education factors from a raw JSON file and loads them into an EducationFactors model.

    Args:
        input_json_path (str): Path to the original raw JSON file.
        extracted_output_path (str): Path where the processed/extracted JSON will be saved.

    Returns:
        EducationFactors: A populated Pydantic model containing structured education-related factors.

    Raises:
        RuntimeError: If extraction or file loading fails.
    """
    try:
        from src.utils import load_json_file
    except ImportError as e:
        logger.error("Failed to import utilities or controller: %s", e)
        raise RuntimeError("Missing required modules for education factor processing") from e

    try:
        logger.info("Extracting education rules from input JSON...")
        extract_education_table(
            input_path=input_json_path,
            output_path=extracted_output_path,
            label_key="Level of Education"
        )
    except Exception as e:
        logger.error("Failed to extract education rules from JSON: %s", e)
        raise RuntimeError("Error extracting education rules") from e

    try:
        logger.info("Loading extracted JSON data into EducationFactors model...")
        success, result = load_json_file(file_path=extracted_output_path)
        education_factors = EducationFactors(**result)
    except Exception as e:
        logger.error("Failed to parse extracted JSON into EducationFactors model: %s", e)
        raise RuntimeError("Error loading education factors from extracted data") from e

    return education_factors

def main():
    """
    Main function to demonstrate extracting and loading education factors.
    """
    from src.helpers import get_settings, Settings
    app_settings: Settings = get_settings()

    input_json_path = os.path.join(app_settings.ORGINA_FACTUES_TAPLE, app_settings.EDUCATION_TAPLE_NAME)
    extracted_output_path = os.path.join(app_settings.EXTRACTION_FACTURES_TAPLE, "education_factors.json")

    try:
        education_factors = get_education_factors(input_json_path, extracted_output_path)
        logger.info("Successfully loaded education factors.")

        # Example access
        print("Bachelor's degree WITH spouse points:", education_factors.bachelors_with_spouse)
        print("PhD WITHOUT spouse points:", education_factors.phd_without_spouse)

    except Exception as e:
        logger.error("Failed to process education factors: %s", e)

if __name__ == "__main__":
    main()
