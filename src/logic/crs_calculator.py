"""
crs_calculator.py

A module to calculate the Comprehensive Ranking System (CRS) core score
by aggregating points from multiple immigration factors like age, education,
language, and work experience.

This class calls individual factor calculators and sums their results.
Includes logging and exception handling for robust operation.
"""

import logging
import os
import sys
from typing import Optional, Dict, Any

# Setup base project path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),  "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to resolve project root: %s", e)
    sys.exit(1)

from src.infra import setup_logging


logger = setup_logging(name="CRS calculator")

class CRSCalculator:
    def __init__(self, has_spouse: bool, canadian_citizen_spouse: bool = False):
        """
        Initialize the CRSCalculator.

        Args:
            has_spouse (bool): Whether the applicant has a spouse.
                It is "True" only if: You have a partner, they are coming in your application, 
                and they are not already Canadian/PR.
                It is "False" only if: You don't have a partner, OR your partner isn't coming 
                with you, OR your partner is already Canadian/PR.
            canadian_citizen_spouse (bool): Whether the spouse is a Canadian citizen.
                Optional flag, used if you want to add spouse-based conditions.
        """
        self.has_spouse = has_spouse
        self.canadian_citizen_spouse = canadian_citizen_spouse
        self.total_points = 0

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
        Calculate total CRS core points by aggregating points from
        age, education, language, and work experience factors.

        Args:
            age (Optional[int]): Applicant's age.
            age_factors (Optional): Model containing age scoring rules.
            education_level (Optional): Education level.
            education_factors (Optional): Education scoring rules.
            first_language_test_name (Optional[str]): First language test name.
            first_language_scores (Optional[Dict[str, float]]): Scores for first language abilities.
            first_language_factors (Optional): First language scoring rules.
            second_language_test_name (Optional[str]): Second language test name.
            second_language_scores (Optional[Dict[str, float]]): Scores for second language abilities.
            second_language_factors (Optional): Second language scoring rules.
            work_experience_years (Optional[int]): Years of Canadian work experience.
            work_experience_factors (Optional): Work experience scoring rules.

        Returns:
            int: Total CRS core points.

        Raises:
            RuntimeError: For unexpected errors during calculation.
        """
        self.total_points = 0

        try:
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
                points = calculate_language_points(
                    first_language_test_name,
                    first_language_scores,
                    self.has_spouse,
                    first_language_factors,
                )
                logger.info(f"First language points: {points}")
                self.total_points += points

            # Second Language Points
            if (
                second_language_test_name
                and second_language_scores
                and second_language_factors
            ):
                from src.immigration_rules import calculate_second_language_points
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


#if __name__ == "__main__":
    # Example usage:
    # Replace DummyFactors with actual loaded models


    # calculator = CRSCalculator(has_spouse=True)

    # try:
    #     total = calculator.calculate_core_score(
    #         age=30,
    #         age_factors=age_factors,
    #         education_level="Bachelor's",
    #         education_factors=education_factors,
    #         first_language_test_name="IELTS",
    #         first_language_scores={"listening": 8.0, "speaking": 7.0, "reading": 7.5, "writing": 6.5},
    #         first_language_factors=first_lang_factors,
    #         second_language_test_name="PTE",
    #         second_language_scores={"listening": 85, "speaking": 87, "reading": 80, "writing": 78},
    #         second_language_factors=second_lang_factors,
    #         work_experience_years=3,
    #         work_experience_factors=work_exp_factors,
    #     )
    #     print(f"Total CRS Core Score: {total}")

    # except RuntimeError as e:
    #     logger.error(f"Failed to calculate CRS score: {e}")
