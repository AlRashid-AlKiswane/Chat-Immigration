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
from src.controllers import extract_second_language_table,convert_score_to_clb

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
        return SecondLanguageFactors(**result) # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise RuntimeError("Second language parsing error") from e

def calculate_second_language_points(
    test_name: str,
    scores: dict,  # {"listening":7.5, "speaking":7.0, "reading":6.5, "writing":6.0}
    has_spouse: bool,
    factors: SecondLanguageFactors,
) -> int:
    """
    Calculate CRS points for second official language.

    Args:
        test_name (str): Language test name (e.g., 'IELTS', 'PTE').
        scores (dict): Dict of user scores for abilities.
        has_spouse (bool): Whether applicant has spouse.
        factors (SecondLanguageFactors): Model with points mapping.
        logger (Logger): Optional logger for debugging.
        
    Returns:
        int: CRS points.
    """

    logger.info(f"Calculating second language points for test '{test_name}', spouse: {has_spouse}")
    logger.debug(f"Raw input scores: {scores}")

    # Validate input
    required_abilities = {"listening", "reading", "writing", "speaking"}
    missing = required_abilities - scores.keys()
    if missing:
        logger.error(f"Missing scores for abilities: {missing}")
        raise ValueError(f"Scores missing for: {', '.join(missing)}")

    # Convert all scores to CLB
    clb_levels = {}
    for ability, score in scores.items():
        clb = convert_score_to_clb(test_name, ability, score)
        clb_levels[ability] = clb
        logger.debug(f"Converted {ability} score {score} -> CLB {clb}")

    # Find the minimum CLB across abilities
    min_clb = min(clb_levels.values())
    logger.debug(f"CLB levels: {clb_levels} | Minimum CLB: {min_clb}")

    # Determine suffix for spouse
    suffix = "with_spouse" if has_spouse else "without_spouse"

    # Map min_clb to points
    if min_clb <= 4:
        attr_name = f"clb_4_or_less_{suffix}"
    elif 5 <= min_clb <= 6:
        attr_name = f"clb_5_or_6_{suffix}"
    elif 7 <= min_clb <= 8:
        attr_name = f"clb_7_or_8_{suffix}"
    else:  # min_clb >= 9
        attr_name = f"clb_9_or_more_{suffix}"

    try:
        points = getattr(factors, attr_name)
        logger.info(f"Second language points = {points} (based on min CLB {min_clb}, attribute '{attr_name}')")
        return points
    except AttributeError as e:
        logger.error(f"Factor attribute '{attr_name}' not found in SecondLanguageFactors: {e}")
        raise RuntimeError(f"Invalid factor mapping for CLB level {min_clb}")

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
        scores = {
        "listening": 6.5,
        "reading": 6.0,
        "writing": 6.0,
        "speaking": 6.5
            }
        test_name="IELTS"
        points = calculate_second_language_points(
        test_name=test_name,
        scores=scores,
        has_spouse=False,
        factors=factors)
        print(f"user secound language final score in {test_name}: {points}")
    except Exception as e:
        logger.error("Processing failed: %s", e)

if __name__ == "__main__":
    main()
