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
from src.enums.value_enums import EducationLevel

logger = setup_logging(name="SPOUSE_EDUCATION_MODELS")


class SpouseEducationFactors(BaseModel):
    """
    Represents spouse education immigration points with/without spouse.
    """

    less_than_secondary_with_spouse: int = Field(
        ..., alias="LESS_THAN_SECONDARY_SCHOOL_HIGH_SCHOOL_WITH_SPOUSE"
    )
    less_than_secondary_without_spouse: int = Field(
        ..., alias="LESS_THAN_SECONDARY_SCHOOL_HIGH_SCHOOL_WITHOUT_SPOUSE"
    )

    secondary_graduation_with_spouse: int = Field(
        ..., alias="SECONDARY_SCHOOL_HIGH_SCHOOL_GRADUATION_WITH_SPOUSE"
    )
    secondary_graduation_without_spouse: int = Field(
        ..., alias="SECONDARY_SCHOOL_HIGH_SCHOOL_GRADUATION_WITHOUT_SPOUSE"
    )

    one_year_post_secondary_with_spouse: int = Field(
        ..., alias="ONE_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITH_SPOUSE"
    )
    one_year_post_secondary_without_spouse: int = Field(
        ..., alias="ONE_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITHOUT_SPOUSE"
    )

    two_year_post_secondary_with_spouse: int = Field(
        ..., alias="TWO_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_IN_SCHOOL_OR_OTHER_INSTITUTE_WITH_SPOUSE"
    )
    two_year_post_secondary_without_spouse: int = Field(
        ..., alias="TWO_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_IN_SCHOOL_OR_OTHER_INSTITUTE_WITHOUT_SPOUSE"
    )

    bachelors_or_three_plus_with_spouse: int = Field(
        ..., alias="BACHELOR_S_DEGREE_OR_A_THREE_OR_MORE_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITH_SPOUSE"
    )
    bachelors_or_three_plus_without_spouse: int = Field(
        ..., alias="BACHELOR_S_DEGREE_OR_A_THREE_OR_MORE_YEAR_PROGRAM_AT_A_UNIVERSITY_COLLEGE_TRADE_OR_TECHNICAL_SCHOOL_OR_OTHER_INSTITUTE_WITHOUT_SPOUSE"
    )

    two_or_more_certificates_with_spouse: int = Field(
        ..., alias="TWO_OR_MORE_CERTIFICATES_DIPLOMAS_OR_DEGREES_ONE_MUST_BE_FOR_A_PROGRAM_OF_THREE_OR_MORE_YEARS_WITH_SPOUSE"
    )
    two_or_more_certificates_without_spouse: int = Field(
        ..., alias="TWO_OR_MORE_CERTIFICATES_DIPLOMAS_OR_DEGREES_ONE_MUST_BE_FOR_A_PROGRAM_OF_THREE_OR_MORE_YEARS_WITHOUT_SPOUSE"
    )

    masters_or_professional_with_spouse: int = Field(
        ..., alias="MASTER_S_DEGREE_OR_PROFESSIONAL_DEGREE_NEEDED_TO_PRACTICE_IN_A_LICENSED_PROFESSION_FOR_PROFESSIONAL_DEGREE_THE_DEGREE_PROGRAM_MUST_HAVE_BEEN_IN_MEDICINE_VETERINARY_MEDICINE_DENTISTRY_OPTOMETRY_LAW_CHIROPRACTIC_MEDICINE_OR_PHARMACY_WITH_SPOUSE"
    )
    masters_or_professional_without_spouse: int = Field(
        ..., alias="MASTER_S_DEGREE_OR_PROFESSIONAL_DEGREE_NEEDED_TO_PRACTICE_IN_A_LICENSED_PROFESSION_FOR_PROFESSIONAL_DEGREE_THE_DEGREE_PROGRAM_MUST_HAVE_BEEN_IN_MEDICINE_VETERINARY_MEDICINE_DENTISTRY_OPTOMETRY_LAW_CHIROPRACTIC_MEDICINE_OR_PHARMACY_WITHOUT_SPOUSE"
    )

    phd_with_spouse: int = Field(
        ..., alias="DOCTORAL_LEVEL_UNIVERSITY_DEGREE_PHD_WITH_SPOUSE"
    )
    phd_without_spouse: int = Field(
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
        return SpouseEducationFactors(**result)  # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise RuntimeError("Spouse education parsing error") from e


def calculate_spouse_education_points(
    education_level: EducationLevel,
    has_spouse: bool,
    factors: SpouseEducationFactors
) -> int:
    """
    Calculate CRS points for spouse's education level.

    Args:
        education_level (EducationLevel): Enum value of spouse's education level.
        has_spouse (bool): True if spouse is included in application, else False.
        factors (SpouseEducationFactors): Loaded scoring factors.

    Returns:
        int: CRS points for spouse education.

    Raises:
        ValueError: If parameters are invalid or education level unknown.
    """
    logger.info(f"Calculating education points for {education_level.name}, spouse: {has_spouse}")

    if not isinstance(education_level, EducationLevel):
        raise ValueError("education_level must be an instance of EducationLevel enum")

    if not isinstance(has_spouse, bool):
        raise ValueError("has_spouse must be a boolean")

    suffix = "with_spouse" if has_spouse else "without_spouse"

    try:
        if education_level == EducationLevel.LESS_THAN_SECONDARY:
            attr_name = f"less_than_secondary_{suffix}"
        elif education_level == EducationLevel.SECONDARY_DIPLOMA:
            attr_name = f"secondary_graduation_{suffix}"
        elif education_level == EducationLevel.ONE_YEAR_POST_SECONDARY:
            attr_name = f"one_year_post_secondary_{suffix}"
        elif education_level == EducationLevel.TWO_YEAR_POST_SECONDARY:
            attr_name = f"two_year_post_secondary_{suffix}"
        elif education_level == EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE:
            attr_name = f"bachelors_or_three_plus_{suffix}"
        elif education_level == EducationLevel.TWO_OR_MORE_CERTIFICATES:
            attr_name = f"two_or_more_certificates_{suffix}"
        elif education_level == EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE:
            attr_name = f"masters_or_professional_{suffix}"
        elif education_level == EducationLevel.PHD:
            attr_name = f"phd_{suffix}"
        else:
            raise ValueError(f"Unknown education level: {education_level}")

        points = getattr(factors, attr_name)
        logger.info(f"Spouse education points for attribute '{attr_name}': {points}")
        return points

    except AttributeError as e:
        logger.error(f"Attribute '{attr_name}' not found in spouse education factors: {e}")
        raise ValueError(f"Invalid spouse education level attribute: {attr_name}") from e


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
        print("PhD WITH spouse:", factors.phd_with_spouse)
        print("Bachelor WITHOUT spouse:", factors.bachelors_or_three_plus_without_spouse)
        education_level = EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE
        has_spouse = True
        points = calculate_spouse_education_points(education_level, has_spouse, factors)
        print(f"Calculated CRS spouse education points for {education_level.name} (has_spouse={has_spouse}): {points}")
    except Exception as e:
        logger.error("Processing failed: %s", e)


if __name__ == "__main__":
    main()
