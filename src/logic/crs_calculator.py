import logging
import os
import sys
from typing import Optional, Dict, Any

# Setup base project path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to resolve project root: %s", e)
    sys.exit(1)

from src.infra import setup_logging
from src.enums.value_enums import EducationLevel

logger = setup_logging(name="CRS calculator")


class CRSCalculator:
    def __init__(self, has_spouse: bool, canadian_citizen_spouse: bool = False ):
        """
        Initialize the CRSCalculator.
        """
        self.has_spouse = has_spouse
        self.canadian_citizen_spouse = canadian_citizen_spouse

        # Core saved values
        self.total_points = 0
        self.age= 0
        self.education_level = None
        self.work_experience_years = None #(outside Canada)
        self.second_language_test_name=None
        self.first_language_test_name=None
        self.min_clb = None


        # use it in work eduction points calculating (jsut canadian work)
        self.canadian_work_experience= False
        self.canadian_work_experience_years=None

        # Spouse saved values
        self.spouse_education_level =None
        self.spouse_work_experience = None
        self.spouse_min_clb = None

        # --- Skill transferability factor models ---
        self.language_education_factors = None
        self.canadian_work_education_factors = None
        self.foreign_work_language_factors = None
        self.foreign_canadian_work_factors = None
        self.certificate_of_qualification_factors = None

        self.has_certificate_of_qualification=False



    def calculate_core_score(
        self,
        age: Optional[int] = None,
        age_factors: Optional[Any] = None,
        education_level: Optional[Any] = None,
        education_factors: Optional[Any] = None,
        first_language_test_name: Optional[str] = None,
        first_language_scores: Optional[Dict[str, float]] = None,
        first_language_factors: Optional[Any] = None,
        second_language_test_name: Optional[str] = None,
        second_language_scores: Optional[Dict[str, float]] = None,
        second_language_factors: Optional[Any] = None,
        work_experience_years: Optional[int] = None,
        work_experience_factors: Optional[Any] = None,
    ) -> int:
        """
        Calculate total CRS core points and save variables for later use.
        """
        self.total_points = 0

        try:
            # Save education and work experience
            self.education_level = education_level
            self.work_experience_years = work_experience_years
            self.age= age

            # Age points
            if age is not None and age_factors is not None:
                from src.immigration_rules import calculate_age_points
                points = calculate_age_points(age, self.has_spouse, age_factors)
                logger.info(f"Age points: {points}")
                self.total_points += points

            # Education Points
            if education_level is not None and education_factors is not None:
                from src.immigration_rules import calculate_education_points
                points = calculate_education_points(
                    education_level, self.has_spouse, education_factors
                )
                logger.info(f"Education points: {points}")
                self.total_points += points

            # First Language Points
            if (
                first_language_test_name
                and first_language_scores
                and first_language_factors
            ):
                from src.immigration_rules import calculate_language_points
                self.first_language_test_name=first_language_test_name
                points, min_clb = calculate_language_points(
                    first_language_test_name,
                    first_language_scores,
                    self.has_spouse,
                    first_language_factors,
                )
                self.min_clb = min_clb
                logger.info(f"First language points: {points}, Min CLB: {min_clb}")
                self.total_points += points

            # Second Language Points
            if (
                second_language_test_name
                and second_language_scores
                and second_language_factors
            ):
                from src.immigration_rules import calculate_second_language_points
                self.second_language_test_name= second_language_test_name
                points = calculate_second_language_points(
                    second_language_test_name,
                    second_language_scores,
                    self.has_spouse,
                    second_language_factors,
                )
                logger.info(f"Second language points: {points}")
                self.total_points += points

            # Work Experience Points
            if work_experience_years is not None and work_experience_factors is not None:
                from src.immigration_rules import calculate_work_experience_points
                points = calculate_work_experience_points(
                    work_experience_years, self.has_spouse, work_experience_factors
                )
                logger.info(f"Work experience points: {points}")
                self.total_points += points

            logger.info(f"Total CRS core score calculated: {self.total_points}")
            return self.total_points

        except ImportError as imp_err:
            logger.error(f"Import error during calculation: {imp_err}")
            raise RuntimeError("Required calculation function imports failed.") from imp_err

        except Exception as exc:
            logger.error(f"Unexpected error during CRS calculation: {exc}")
            raise RuntimeError("CRS calculation failed.") from exc

    def calculate_spouse_score(
        self,
        spouse_language_test_name: str,
        spouse_language_scores:Dict[str, float],
        spouse_language_factors: Any,
        spouse_education_factors:Any,
        spouse_work_factors: Any,
        spouse_education_level: EducationLevel,
        spouse_work_experience: int ,
    ) -> int:
        """
        Calculate and save spouse's points.
        """
        spouse_points = 0

        # Save education and work experience
        self.spouse_education_level = spouse_education_level
        from src.immigration_rules import calculate_spouse_education_points
        points = calculate_spouse_education_points(education_level=spouse_education_level,has_spouse=True,factors=spouse_education_factors) # type: ignore
        spouse_points +=points

        self.spouse_work_experience = spouse_work_experience
        from src.immigration_rules import calculate_spouse_work_experience_points
        points= calculate_spouse_work_experience_points(years_of_experience=spouse_work_experience,has_spouse=True,factors=spouse_work_factors) # type: ignore
        spouse_points += points

        if spouse_language_test_name and spouse_language_scores and spouse_language_factors:
            from src.immigration_rules import calculate_spouse_language_points
            points, spouse_min_clb = calculate_spouse_language_points(
                spouse_language_test_name,
                spouse_language_scores,
                self.has_spouse,
                spouse_language_factors,
            )
            self.spouse_min_clb = spouse_min_clb
            logger.info(f"Spouse language points: {points}, Min CLB: {spouse_min_clb}")
            spouse_points += points

        return spouse_points
    
    def calculate_skill_transferability(self, canadian_work_experience_years: Optional[int], has_certificate_of_qualification : Optional[bool] = False) -> int:
        """
            Calculate Skill Transferability Points in the correct order:
        1. Language + Education
        2. Canadian Work Experience + Education
        3. Foreign Work Experience + Language
        4. Foreign Work Experience + Canadian Work Experience
        5. Certificate of Qualification + Language (if applicable)

        Skips any calculation if the required data is missing.
            """
        total_transfer_points = 0
        


        from src.immigration_rules import (
            calculate_language_education_points,
            calculate_canadian_work_education_points,
            calculate_foreign_work_language_points,
            calculate_foreign_canadian_work_points,
            calculate_certificate_of_qualification_points,
        )

        # 1. Language + Education
        if self.education_level and self.min_clb is not None and self.language_education_factors:
            total_transfer_points += calculate_language_education_points(
                self.education_level, self.min_clb, self.language_education_factors
            )

        # 2. Canadian Work Experience + Education
        if (
            self.education_level
            and canadian_work_experience_years is not None
            and self.canadian_work_education_factors
        ):
            self.canadian_work_experience_years=canadian_work_experience_years
            total_transfer_points += calculate_canadian_work_education_points(
                self.education_level,
                self.canadian_work_experience_years,
                self.canadian_work_education_factors,
            )

        # 3. Foreign Work Experience + Language
        if (
            self.work_experience_years is not None
            and self.min_clb is not None
            and self.foreign_work_language_factors
        ):
            total_transfer_points += calculate_foreign_work_language_points(
                self.work_experience_years,
                self.min_clb,
                self.foreign_work_language_factors,
            )

        # 4. Foreign Work Experience + Canadian Work Experience
        if (
            self.work_experience_years is not None
            and self.canadian_work_experience_years is not None
            and self.foreign_canadian_work_factors
        ):
            total_transfer_points += calculate_foreign_canadian_work_points(
                self.work_experience_years,
                self.canadian_work_experience_years,
                self.foreign_canadian_work_factors,
            )

        # 5. Certificate of Qualification + Language
        if has_certificate_of_qualification and self.min_clb is not None and self.certificate_of_qualification_factors:
            self.has_certificate_of_qualification=has_certificate_of_qualification
            total_transfer_points += calculate_certificate_of_qualification_points(
                self.min_clb, self.certificate_of_qualification_factors
            )

        logger.info(f"Skill transferability points: {total_transfer_points}")
        return total_transfer_points


