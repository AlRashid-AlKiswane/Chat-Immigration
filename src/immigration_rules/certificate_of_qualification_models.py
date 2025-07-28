import os
import sys
import logging
from pydantic import BaseModel, Field

# Setup for main directory and logger
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),  "../.."))
    sys.path.append(MAIN_DIR)
except Exception as e:
    print("Directory setup error:", e)
    sys.exit(1)

from src.infra import setup_logging

logger = setup_logging(name="CERTIFICATE_QUALIFICATION_MODEL")

from src.helpers import get_settings, Settings
settings: Settings = get_settings()

input_path = os.path.join(settings.ORGINA_FACTUES_TAPLE, settings.CERTIFICATE_QUALIFICATION_TABLE_NAME)
output_path = os.path.join(settings.EXTRACTION_FACTURES_TAPLE, "certificate_of_qualification_points.json")


class CertificateOfQualificationFactors(BaseModel):
    """
    Points for certificate of qualification + CLB level.
    """

    clb_5_or_6: int = Field(..., alias="CERTIFICATE_CLB_5_TO_6")
    clb_7_or_more: int = Field(..., alias="CERTIFICATE_CLB_7_OR_MORE")

    class Config:
        validate_by_name = True


def get_certificate_of_qualification_points(input_json: str =input_path, extracted_json: str= output_path) -> CertificateOfQualificationFactors:
    from src.utils import load_json_file
    from src.controllers import extract_certificate_of_qualification

    try:
        logger.info("Extracting certificate of qualification points...")
        extract_certificate_of_qualification(
            input_path=input_json,
            output_path=extracted_json,
        )
    except Exception as e:
        logger.error("Extraction failed: %s", e)
        raise

    try:
        success, data = load_json_file(file_path=extracted_json)
        return CertificateOfQualificationFactors(**data) # type: ignore
    except Exception as e:
        logger.error("Model loading failed: %s", e)
        raise

def calculate_certificate_of_qualification_points(
    clb_level: int,
    factors: CertificateOfQualificationFactors
) -> int:
    """
    Calculate CRS points for the certificate of qualification based on CLB level.

    Args:
        clb_level (int): Canadian Language Benchmark (CLB) level of the applicant.
            Should be a positive integer (e.g., 5, 6, 7, or higher).
        factors (CertificateOfQualificationFactors): Model containing CRS points 
            for certificate qualification based on CLB levels.

    Returns:
        int: CRS points awarded for the certificate of qualification.

    Raises:
        ValueError: If clb_level is less than 5 (certificate points start from CLB 5).
        AttributeError: If the corresponding attribute is missing in the factors model.
    """
    if clb_level < 5:
        raise ValueError("CLB level must be 5 or higher for certificate qualification points")

    if 5 <= clb_level <= 6:
        attr_name = "clb_5_or_6"
    else:  # clb_level 7 or higher
        attr_name = "clb_7_or_more"

    try:
        points = getattr(factors, attr_name)
    except AttributeError as e:
        raise AttributeError(f"Attribute '{attr_name}' missing in CertificateOfQualificationFactors model") from e

    return points



if __name__ == "__main__":


    try:
        model = get_certificate_of_qualification_points(input_path, output_path)
        print("Certificate of Qualification model:")
        print(model)
        clb = 7
        points = calculate_certificate_of_qualification_points(clb_level=clb, factors=model)
        print(f"CRS points for certificate of qualification at CLB {clb}: {points}")
    except Exception as e:
        logger.error("Processing failed: %s", e)
