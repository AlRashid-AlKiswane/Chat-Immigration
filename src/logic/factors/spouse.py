"""
Spouse/Common-Law Partner Factors for CRS Scoring.
Includes education, language, and Canadian work experience.
"""

import logging
from typing import Dict

from src.logs import setup_logging
from src.enums.value_enums import EducationLevel, LanguageAbility
from src.logic.factors import CRSFactor

logger = setup_logging()


class SpouseEducationFactor(CRSFactor):
    """
    Calculates CRS points for spouse/common-law partner's education.
    """

    def score(self, level: EducationLevel) -> int:
        """
        Args:
            level: EducationLevel enum

        Returns:
            CRS points for spouse education

        Raises:
            TypeError: If level is not an EducationLevel
        """
        try:
            if not isinstance(level, EducationLevel):
                raise TypeError(f"Expected EducationLevel enum, got {type(level)}")

            logger.debug(f"Scoring spouse education level: {level.value}")
            return self.rules.get(level.value, 0)

        except Exception as e:
            logger.error(f"Failed to score spouse education: {e}")
            raise


class SpouseLanguageFactor(CRSFactor):
    """
    Calculates CRS points for spouse's language abilities.
    """

    def score(self, abilities: Dict[LanguageAbility, int]) -> int:
        """
        Args:
            abilities: Dict of 4 language skills with CLB levels

        Returns:
            CRS points for spouse language

        Raises:
            TypeError or ValueError on invalid input
        """
        try:
            self._validate_abilities(abilities)

            total = sum(self._score_clb(clb) for clb in abilities.values())
            logger.debug(f"Spouse language score: {total}")
            return total

        except Exception as e:
            logger.error(f"Error scoring spouse language: {e}")
            raise

    def _score_clb(self, clb: int) -> int:
        if clb <= 4:
            return self.rules["clb_4_or_less"]
        elif clb <= 6:
            return self.rules["clb_5_or_6"]
        elif clb == 7:
            return self.rules["clb_7"]
        elif clb == 8:
            return self.rules["clb_8"]
        elif clb == 9:
            return self.rules["clb_9"]
        else:
            return self.rules["clb_10_or_more"]

    def _validate_abilities(self, abilities: Dict[LanguageAbility, int]):
        if not isinstance(abilities, dict):
            raise TypeError("Spouse language abilities must be a dictionary")
        if not all(isinstance(k, LanguageAbility) for k in abilities.keys()):
            raise TypeError("Keys must be LanguageAbility enums")
        if not all(isinstance(v, int) and 1 <= v <= 12 for v in abilities.values()):
            raise ValueError("CLB levels must be integers between 1 and 12")


class SpouseExperienceFactor(CRSFactor):
    """
    Calculates CRS points for spouse's Canadian work experience.
    """

    def score(self, years: int) -> int:
        """
        Args:
            years: Full years of experience (0–5+)

        Returns:
            CRS points for spouse's Canadian work experience

        Raises:
            ValueError: Invalid input
        """
        try:
            if not isinstance(years, int) or years < 0:
                raise ValueError("Years must be a non-negative integer")

            logger.debug(f"Scoring spouse Canadian experience: {years} years")

            if years == 0:
                return self.rules["none_or_less_than_a_year"]
            elif years == 1:
                return self.rules["1_year"]
            elif years == 2:
                return self.rules["2_years"]
            elif years == 3:
                return self.rules["3_years"]
            elif years == 4:
                return self.rules["4_years"]
            else:
                return self.rules["5_years_or_more"]

        except Exception as e:
            logger.error(f"Error scoring spouse experience: {e}")
            raise
