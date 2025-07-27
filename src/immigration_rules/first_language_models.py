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

import os
import sys
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Dict

# Setup base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),  "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set main directory path: %s", e)
    sys.exit(1)

from src.infra import setup_logging
from src.controllers import extract_education_table ,convert_score_to_clb
logger = setup_logging(name="FIRST_LANGUAGE_MODELS")

from src.helpers import get_settings, Settings
app_settings: Settings = get_settings()

input_json_path = os.path.join(app_settings.ORGINA_FACTUES_TAPLE, app_settings.FIERST_LANGUAGE_TAPLE_NAME)
extracted_output_path = os.path.join(app_settings.EXTRACTION_FACTURES_TAPLE, "first_language_factors.json")

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

def get_first_language_factors(input_json_path: str =input_json_path, extracted_output_path: str=extracted_output_path) -> FirstLanguageFactors:
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
        return FirstLanguageFactors(**result) # type: ignore

    except Exception as e:
        logger.error("Failed to parse JSON: %s", e)
        raise RuntimeError("Language factors model loading failed") from e
    
def calculate_language_points(
    test_name: str,
    user_scores: Dict[str, float],
    has_spouse: bool,
    language_factors: "FirstLanguageFactors",
) -> tuple[int, int]:
    """
    Calculate total CRS language points and return the minimum CLB level.

    Args:
        test_name: Name of the language test (IELTS, CELPIP, TEF, TCF, PTE).
        user_scores: Dict with keys ["reading", "writing", "listening", "speaking"] and numeric scores.
        has_spouse: True if the applicant has a spouse.
        language_factors: FirstLanguageFactors model loaded from JSON table.

    Returns:
        tuple[int, int]: (total_points, min_clb)
    """
    logger.info(f"Calculating language points for {test_name}, spouse={has_spouse}")
    suffix = "with_spouse" if has_spouse else "without_spouse"

    total_points = 0
    clb_levels = []

    for ability, score in user_scores.items():
        # 1) Convert test score to CLB
        clb_level = convert_score_to_clb(test_name, ability, score)
        clb_levels.append(clb_level)
        logger.debug(f"{ability}: score={score} => CLB={clb_level}")

        # 2) Determine attribute name from CLB level
        if clb_level == 0:  # below CLB 4
            attr_name = f"less_than_clb_4_{suffix}"
        elif clb_level in [4, 5]:
            attr_name = f"clb_4_or_5_{suffix}"
        elif clb_level == 6:
            attr_name = f"clb_6_{suffix}"
        elif clb_level == 7:
            attr_name = f"clb_7_{suffix}"
        elif clb_level == 8:
            attr_name = f"clb_8_{suffix}"
        elif clb_level == 9:
            attr_name = f"clb_9_{suffix}"
        else:  # CLB 10 or more
            attr_name = f"clb_10_or_more_{suffix}"

        # 3) Fetch points from language_factors
        try:
            points = getattr(language_factors, attr_name)
        except AttributeError:
            logger.error(f"Attribute '{attr_name}' not found in language factors")
            points = 0

        total_points += points
        logger.debug(f"{ability}: CLB={clb_level} -> {points} points")

    min_clb = min(clb_levels) if clb_levels else 0
    logger.info(f"Total language points: {total_points}, Min CLB: {min_clb}")

    return total_points, min_clb

def main():
    """
    Run an example of loading first language factors using project settings.
    """


    try:
        factors = get_first_language_factors(input_json_path, extracted_output_path)
        logger.info("Language factors loaded successfully.")
        print("CLB 9 WITH spouse:", factors.clb_9_with_spouse)
        print("CLB 10+ WITHOUT spouse:", factors.clb_10_or_more_without_spouse)
        print("calculate language score:")
        user_scores = {"reading": 75.0, "writing": 85.0, "listening": 70.0, "speaking": 77.0}
        language_test_name= "PTE"
        print(f"calculate language points for user score {user_scores} for {language_test_name} test")

        points = calculate_language_points(language_test_name, user_scores, has_spouse=False, language_factors=factors)
        print(f"language score result: {points}")
    except Exception as e:
        logger.error("Failed to load language data: %s", e)

if __name__ == "__main__":
    main()
