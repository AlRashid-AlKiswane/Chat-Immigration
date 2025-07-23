"""
spouse_education_models.py

Defines the `SpouseEducationFactors` model representing immigration points for
spouse's level of education with and without a spouse. Includes logic to
extract and load rule data from JSON.

- Structured schema for spouse education scoring
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
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to resolve project root: %s", e)
    sys.exit(1)

from src.infra import setup_logging
from src.controllers import extract_spouse_education_table

logger = setup_logging(name="SPOUSE_EDUCATION_MODELS")


class SpouseEducationFactors(BaseModel):
    """
    Represents spouse education immigration points with/without spouse.
    """

    less_than_secondary_school_high_school_with_spouse: int = Field(
        ..., alias="LESS_THAN_SECONDARY_SCHOOL_HIGH_SCHOOL_WITH_SPOUSE"
    )
    less_than_secondary_school_high_school_without_spouse: int = Field(
        ..., alias="LESS_THAN_SECONDARY_SCHOOL_HIGH_SCHOOL_WITHOUT_SPOUSE"
    )

    secondary_school_high_school_graduation_with_spouse: int = Field(
        ..., alias="SECONDARY_SCHOOL_HIGH_SCHOOL_GRADUATION_WITH_SPOUSE"
    )
    secondary_school_high_school_graduation_without_spouse: int = Field(
        ..., alias="SECONDARY_SCHOOL_HIGH_SCHOOL_GRADUATION_WITHOUT_SPOUSE"
    )

    one_year_program_university_college_trade_or_technical_school_or_other_institute_with_spouse: int = Field(
        ..., alias="ONE_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITH_SPOUSE"
    )
    one_year_program_university_college_trade_or_technical_school_or_other_institute_without_spouse: int = Field(
        ..., alias="ONE_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITHOUT_SPOUSE"
    )

    two_year_program_university_college_trade_or_technical_in_school_or_other_institute_with_spouse: int = Field(
        ..., alias="TWO_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_IN_SCHOOL_OR_OTHER_INSTITUTE_WITH_SPOUSE"
    )
    two_year_program_university_college_trade_or_technical_in_school_or_other_institute_without_spouse: int = Field(
        ..., alias="TWO_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_IN_SCHOOL_OR_OTHER_INSTITUTE_WITHOUT_SPOUSE"
    )

    bachelors_or_three_plus_year_program_with_spouse: int = Field(
        ..., alias="BACHELOR_S_DEGREE_OR_A_THREE_OR_MORE_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITH_SPOUSE"
    )
    bachelors_or_three_plus_year_program_without_spouse: int = Field(
        ..., alias="BACHELOR_S_DEGREE_OR_A_THREE_OR_MORE_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITHOUT_SPOUSE"
    )

    two_or_more_certificates_diplomas_one_three_plus_years_with_spouse: int = Field(
        ..., alias="TWO_OR_MORE_CERTIFICATES_DIPLOMAS_OR_DEGREES_ONE_MUST_BE_FOR_A_PROGRAM_OF_THREE_OR_MORE_YEARS_WITH_SPOUSE"
    )
    two_or_more_certificates_diplomas_one_three_plus_years_without_spouse: int = Field(
        ..., alias="TWO_OR_MORE_CERTIFICATES_DIPLOMAS_OR_DEGREES_ONE_MUST_BE_FOR_A_PROGRAM_OF_THREE_OR_MORE_YEARS_WITHOUT_SPOUSE"
    )

    masters_or_professional_degree_with_spouse: int = Field(
        ..., alias="MASTER_S_DEGREE_OR_PROFESSIONAL_DEGREE_NEEDED_TO_PRACTICE_IN_A_LICENSED_PROFESSION_FOR_PROFESSIONAL_DEGREE_THE_DEGREE_PROGRAM_MUST_HAVE_BEEN_IN_MEDICINE_VETERINARY_MEDICINE_DENTISTRY_OPTOMETRY_LAW_CHIROPRACTIC_MEDICINE_OR_PHARMACY_WITH_SPOUSE"
    )
    masters_or_professional_degree_without_spouse: int = Field(
        ..., alias="MASTER_S_DEGREE_OR_PROFESSIONAL_DEGREE_NEEDED_TO_PRACTICE_IN_A_LICENSED_PROFESSION_FOR_PROFESSIONAL_DEGREE_THE_DEGREE_PROGRAM_MUST_HAVE_BEEN_IN_MEDICINE_VETERINARY_MEDICINE_DENTISTRY_OPTOMETRY_LAW_CHIROPRACTIC_MEDICINE_OR_PHARMACY_WITHOUT_SPOUSE"
    )

    doctoral_level_university_degree_phd_with_spouse: int = Field(
        ..., alias="DOCTORAL_LEVEL_UNIVERSITY_DEGREE_PHD_WITH_SPOUSE"
    )
    doctoral_level_university_degree_phd_without_spouse: int = Field(
        ..., alias="DOCTORAL_LEVEL_UNIVERSITY_DEGREE_PHD_WITHOUT_SPOUSE"
    )

    class Config:
        validate_by_name = True


def get_spouse_education_factors(input_json_path: str, extracted_output_path: str) -> SpouseEducationFactors:
    """
    Extracts spouse education rule data and loads it into a model.

    Args:
        input_json_path (str): Path to the original JSON file.
        extracted_output_path (str): Path to save the flattened result.

    Returns:
        SpouseEducationFactors: The populated model.

    Raises:
        RuntimeError: On extraction or parsing error.
    """
    try:
        from src.utils import load_json_file
    except ImportError as e:
        logger.error("Import failed: %s", e)
        raise RuntimeError("Utility import failure") from e

    try:
        logger.info("Extracting spouse education rules...")
        extract_spouse_education_table(
            input_path=input_json_path,
            output_path=extracted_output_path,
            label_key="Spouse’s or common-law partner’s level of education"
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise RuntimeError("Spouse education extraction error") from e

    try:
        logger.info("Loading extracted JSON into model...")
        success, result = load_json_file(file_path=extracted_output_path)
        return SpouseEducationFactors(**result)
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise RuntimeError("Spouse education parsing error") from e


def main():
    """
    Demonstrates usage of the spouse education rule parser.
    """
    from src.helpers import get_settings, Settings
    app_settings: Settings = get_settings()

    input_json_path = os.path.join(app_settings.ORGINA_FACTUES_TAPLE, app_settings.SPOUSE_EDUCATION_TABLE_NAME)
    extracted_output_path = os.path.join(app_settings.EXTRACTION_FACTURES_TAPLE, "spouse_education_factors.json")

    try:
        factors = get_spouse_education_factors(input_json_path, extracted_output_path)
        logger.info("Loaded spouse education factors.")
        print("PhD WITH spouse:", factors.doctoral_level_university_degree_phd_with_spouse)
        print("Bachelor WITHOUT spouse:", factors.bachelors_or_three_plus_year_program_without_spouse)
    except Exception as e:
        logger.error("Processing failed: %s", e)


if __name__ == "__main__":
    main()
