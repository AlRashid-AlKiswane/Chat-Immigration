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
from src.controllers import convert_score_to_clb

logger = setup_logging(name="SPOUSE_LANGUAGE_MODELS_FACTORS")

from src.helpers import get_settings, Settings
app_settings: Settings = get_settings()

input_json_path = os.path.join(app_settings.ORGINA_FACTUES_TAPLE, app_settings.SPOUSE_LANGUAGE_TABLE_NAME)
extracted_output_path = os.path.join(app_settings.EXTRACTION_FACTURES_TAPLE, "spouse_language_factors.json")

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

def get_spouse_language_factors(input_json_path: str =input_json_path, extracted_output_path: str=extracted_output_path) -> SpouseLanguageFactors:
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
        return SpouseLanguageFactors(**result) # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise RuntimeError("Spouse language parsing error") from e

def calculate_spouse_language_points(
    test_name: str,
    user_score: dict,
    has_spouse: bool,
    factors: SpouseLanguageFactors
) -> tuple[int, int]:
    """
    Calculate CRS points for spouse's language abilities (reading, writing,
    speaking, and listening) and return the minimum CLB level.

    Args:
        test_name (str): Name of the language test (e.g., IELTS, CELPIP).
        user_score (dict): Dictionary of ability -> score.
                           Example: {"reading": 6.5, "writing": 6.0, "speaking": 6.5, "listening": 7.0}
        has_spouse (bool): Whether the spouse is included in the application.
        factors (SpouseLanguageFactors): Loaded scoring factors model.

    Returns:
        tuple[int, int]: (Total CRS points, Minimum CLB level)

    Raises:
        ValueError: If parameters are invalid or mapping fails.
    """
    logger.info(
        f"Calculating spouse language points for test={test_name}, "
        f"scores={user_score}, spouse included={has_spouse}"
    )

    if not isinstance(user_score, dict) or not user_score:
        raise ValueError("user_score must be a non-empty dictionary of ability -> score")

    if not isinstance(has_spouse, bool):
        raise ValueError("has_spouse must be a boolean")

    total_points = 0
    clb_levels = []
    suffix = "with_spouse" if has_spouse else "without_spouse"

    for ability, score in user_score.items():
        # Convert the raw test score to CLB level
        clb_level = convert_score_to_clb(test_name, ability, score)
        clb_levels.append(clb_level)
        logger.debug(f"Ability={ability}: raw_score={score} => CLB={clb_level}")

        # Map the CLB level to the correct attribute in the factors model
        if clb_level <= 4:
            attr_name = f"clb_4_or_less_{suffix}"
        elif clb_level in [5, 6]:
            attr_name = f"clb_5_or_6_{suffix}"
        elif clb_level in [7, 8]:
            attr_name = f"clb_7_or_8_{suffix}"
        else:  # CLB 9 or higher
            attr_name = f"clb_9_or_more_{suffix}"

        # Add the points for this ability
        try:
            points = getattr(factors, attr_name)
            total_points += points
            logger.info(f"{ability} -> attribute '{attr_name}' => {points} points")

        except AttributeError as e:
            logger.error(f"Attribute '{attr_name}' not found in spouse language factors: {e}")
            raise ValueError(f"Invalid spouse language attribute: {attr_name}") from e

    min_clb = min(clb_levels) if clb_levels else 0
    logger.info(f"Total spouse language points: {total_points}, Min CLB: {min_clb}")

    return total_points, min_clb


def main():
    """
    Demonstrates usage of the spouse language rule parser.
    """


    try:
        factors = get_spouse_language_factors(input_json_path, extracted_output_path)
        logger.info("Loaded spouse language factors.")
        print("CLB 9+ WITH spouse:", factors.clb_9_or_more_with_spouse)
        print("CLB 5-6 WITHOUT spouse:", factors.clb_5_or_6_without_spouse)

         # Example spouse language scores
        test_name = "IELTS"
        user_score = {
            "reading": 6.5,
            "writing": 6.0,
            "speaking": 6.5,
            "listening": 7.0
        }
        has_spouse = False

        # Calculate spouse language points
        total_points = calculate_spouse_language_points(
            test_name=test_name,
            user_score=user_score,
            has_spouse=has_spouse,
            factors=factors
        )

        print(f"Total spouse language points: {total_points}")
    except Exception as e:
        logger.error("Processing failed: %s", e)


if __name__ == "__main__":
    main()
