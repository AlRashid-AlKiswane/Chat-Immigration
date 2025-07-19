"""

Core Human Capital Factors for Canada's Comprehensive Ranking System (CRS)
This module implements scoring for age, education, language proficiency, and Canadian work experience.

"""
import logging
import os
import sys
from typing import Dict, Optional

try:
    MAIN_DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.infra import setup_logging
from src.enums.value_enums import EducationLevel,LanguageAbility
from src.logic.factors import CRSFactor


logger = setup_logging()


class AgeFactor(CRSFactor):
    """
    Calculates points for age factor in CRS.
    
    Rules:
    - Points vary based on whether applicant has spouse/common-law partner
    - Maximum points for ages 20-29
    - No points for age 45+
    """
    
    def score(self, age: int, has_spouse: bool) -> int:
        """
        Calculate age-based CRS points.
        
        Args:
            age: Applicant's age (17-45+)
            has_spouse: Whether applicant has spouse/common-law partner
            
        Returns:
            CRS points for age factor
            
        Raises:
            ValueError: If age is negative or invalid
            
        Examples:
            >>> age_factor.score(28, False)
            110
            >>> age_factor.score(35, True)
            70
        """
        try:
            if not isinstance(age, int) or age < 0:
                raise ValueError("Age must be a positive integer")
                
            key = "with_spouse" if has_spouse else "without_spouse"
            ruleset = self.rules[key]
            
            logger.debug(f"Calculating age score for {age} (spouse: {has_spouse})")
            
            if age <= 17:
                return ruleset["17_or_less"]
            elif 20 <= age <= 29:
                return ruleset["20-29"]
            elif age >= 45:
                return ruleset["45_or_older"]
            else:
                return ruleset.get(str(age), 0)
                
        except Exception as e:
            logger.error(f"Error calculating age score: {e}")
            raise

class EducationFactor(CRSFactor):
    """
    Calculates points for education level in CRS.
    
    Rules:
    - Points vary based on education level and spouse status
    - Higher education levels receive more points
    """
    
    def score(self, level: EducationLevel, has_spouse: bool) -> int:
        """
        Calculate education-based CRS points.
        
        Args:
            level: EducationLevel enum value
            has_spouse: Whether applicant has spouse/common-law partner
            
        Returns:
            CRS points for education factor
            
        Raises:
            TypeError: If invalid enum value is provided
            
        Examples:
            >>> education_factor.score(EducationLevel.PHD, False)
            150
        """
        try:
            if not isinstance(level, EducationLevel):
                raise TypeError(
                    f"Invalid education level. Must be EducationLevel enum. "
                    f"Valid levels: {EducationLevel.values()}"
                )
                
            key = "with_spouse" if has_spouse else "without_spouse"
            ruleset = self.rules[key]
            
            logger.debug(f"Calculating education score for {level.value} (spouse: {has_spouse})")
            
            return ruleset.get(level.value, 0)
            
        except Exception as e:
            logger.error(f"Error calculating education score: {e}")
            raise

class LanguageFactor(CRSFactor):
    """
    Calculates points for language proficiency in CRS.
    
    Rules:
    - Evaluates all four language abilities (reading, writing, listening, speaking)
    - Second language points only awarded if all abilities meet CLB 5+
    - Points vary based on spouse status
    """
    
    def score(self, 
             abilities: Dict[LanguageAbility, int], 
             second_language_abilities: Optional[Dict[LanguageAbility, int]] = None, 
             has_spouse: bool = False) -> int:
        """
        Calculate language proficiency CRS points.
        
        Args:
            abilities: Dict mapping LanguageAbility to CLB levels
            second_language_abilities: Optional second language abilities
            has_spouse: Whether applicant has spouse/common-law partner
            
        Returns:
            Total language proficiency CRS points
            
        Raises:
            ValueError: If missing abilities or invalid CLB levels
            TypeError: If invalid ability keys are provided
            
        Examples:
            >>> lang_factor.score(
                {LanguageAbility.READING: 8, LanguageAbility.WRITING: 7, ...},
                None,
                False
            )
            92
        """
        try:
            # Validate first language abilities
            self._validate_abilities(abilities, "First language")
            
            # Calculate first language scores
            first_lang_scores = [
                self._get_ability_score('first_language', abilities[ability], has_spouse)
                for ability in LanguageAbility
            ]
            
            # Calculate second language scores if provided
            second_lang_scores = [0, 0, 0, 0]
            if second_language_abilities:
                self._validate_abilities(second_language_abilities, "Second language")
                if all(clb >= 5 for clb in second_language_abilities.values()):
                    second_lang_scores = [
                        self._get_ability_score('second_language', clb, has_spouse)
                        for clb in second_language_abilities.values()
                    ]
                else:
                    logger.info("Second language not qualified - minimum CLB 5 not met for all abilities")
            
            total_score = sum(first_lang_scores) + sum(second_lang_scores)
            logger.debug(f"Calculated language score: {total_score}")
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error calculating language score: {e}")
            raise
    
    def _validate_abilities(self, abilities: Dict[LanguageAbility, int], language_name: str):
        """Validate language abilities structure and CLB levels."""
        if not isinstance(abilities, dict):
            raise ValueError(f"{language_name} abilities must be a dictionary")
            
        if not all(isinstance(ability, LanguageAbility) for ability in abilities.keys()):
            raise TypeError(
                f"{language_name} abilities must use LanguageAbility enum keys. "
                f"Valid abilities: {LanguageAbility.values()}"
            )
            
        if any(clb < 1 or clb > 12 for clb in abilities.values()):
            raise ValueError(
                f"All {language_name} CLB levels must be integers between 1-12"
            )
    
    def _get_ability_score(self, language_type: str, clb: int, has_spouse: bool) -> int:
        """Get score for an individual language ability."""
        try:
            if not 1 <= clb <= 12:
                raise ValueError(f"Invalid CLB level: {clb}. Must be between 1-12")
                
            key = "with_spouse" if has_spouse else "without_spouse"
            ruleset = self.rules[language_type][key]
            
            # Map CLB to score bracket
            if clb <= 4:
                return ruleset["clb_4_or_less"]
            elif clb <= 6:
                return ruleset["clb_5_or_6"]
            elif clb == 7:
                return ruleset["clb_7"]
            elif clb == 8:
                return ruleset["clb_8"]
            elif clb == 9:
                return ruleset["clb_9"]
            else:  # CLB 10+
                return ruleset["clb_10_or_more"]
                
        except Exception as e:
            logger.error(f"Error getting {language_type} score for CLB {clb}: {e}")
            raise



class CanadianExperienceFactor(CRSFactor):
    """
    Calculates points for Canadian work experience in CRS.
    
    Rules:
    - Points increase with years of Canadian work experience
    - Maximum points for 5+ years
    - Points vary based on spouse status
    """
    
    def score(self, years: int, has_spouse: bool) -> int:
        """
        Calculate Canadian work experience CRS points.
        
        Args:
            years: Full years of Canadian work experience (0-5+)
            has_spouse: Whether applicant has spouse/common-law partner
            
        Returns:
            CRS points for Canadian work experience
            
        Raises:
            ValueError: If years is negative
            
        Examples:
            >>> exp_factor.score(3, True)
            56
        """
        try:
            if not isinstance(years, int) or years < 0:
                raise ValueError("Years of experience must be a non-negative integer")
                
            key = "with_spouse" if has_spouse else "without_spouse"
            ruleset = self.rules[key]
            
            logger.debug(f"Calculating Canadian experience for {years} years (spouse: {has_spouse})")
            
            if years == 0:
                return ruleset["none_or_less_than_a_year"]
            elif years == 1:
                return ruleset["1_year"]
            elif years == 2:
                return ruleset["2_years"]
            elif years == 3:
                return ruleset["3_years"]
            elif years == 4:
                return ruleset["4_years"]
            else:
                return ruleset["5_years_or_more"]
                
        except Exception as e:
            logger.error(f"Error calculating Canadian experience score: {e}")
            raise

#if __name__=="__main__":
