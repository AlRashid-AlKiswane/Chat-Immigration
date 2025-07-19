"""
Transferability Factors for Canada's Comprehensive Ranking System (CRS)
This module implements scoring for foreign work experience, education, and language proficiency combinations.
"""

import logging
from typing import Dict
import os
import sys


try:
    MAIN_DIR = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)

from src.infra import setup_logging
from src.logic.factors import CRSFactor

logger = setup_logging()


class TransferabilityFactor(CRSFactor):
    """
    Calculates points for transferability factors in CRS.
    
    Rules:
    - Combines foreign work experience with language proficiency
    - Evaluates trade certificates with language proficiency
    - Points awarded based on CLB levels and qualification status
    """

    def score(self, rules_key: str, sub_key: str, level: str) -> int:
        """
        Generic scoring method for transferability factors.
        
        Args:
            rules_key: Main category key in rules (e.g. "foreign_work_experience")
            sub_key: Sub-category key in rules (e.g. "with_official_language_proficiency")
            level: Specific level to score (e.g. "clb_9_or_higher")
            
        Returns:
            CRS points for the specified factor combination
            
        Examples:
            >>> transfer_factor.score("foreign_work_experience", "with_official_language_proficiency", "clb_7_or_higher")
            25
        """
        try:
            return self.rules[rules_key].get(sub_key, {}).get(level, 0)
        except Exception as e:
            logger.error(f"Error calculating transferability score: {e}")
            raise

    def score_foreign_exp_lang(self, clb: int) -> int:
        """
        Calculate points for foreign work experience with language proficiency.
        
        Args:
            clb: Comprehensive Language Benchmark level (1-12)
            
        Returns:
            CRS points for foreign experience with language proficiency
            
        Raises:
            ValueError: If CLB level is invalid
            
        Examples:
            >>> transfer_factor.score_foreign_exp_lang(8)
            25
        """
        try:
            if not 1 <= clb <= 12:
                raise ValueError("CLB level must be between 1-12")
                
            logger.debug(f"Calculating foreign work experience with CLB {clb}")
            
            if clb >= 9:
                return self.rules["foreign_work_experience"]["with_official_language_proficiency"]["clb_9_or_higher"]
            elif clb >= 7:
                return self.rules["foreign_work_experience"]["with_official_language_proficiency"]["clb_7_or_higher"]
            return 0
                
        except Exception as e:
            logger.error(f"Error calculating foreign experience with language score: {e}")
            raise

    def score_trade_cert_lang(self, has_cert: bool, lang_ok: bool) -> int:
        """
        Calculate points for trade certificate with language proficiency.
        
        Args:
            has_cert: Whether applicant has a certificate of qualification
            lang_ok: Whether language proficiency requirements are met
            
        Returns:
            CRS points for trade certificate with language
            
        Examples:
            >>> transfer_factor.score_trade_cert_lang(True, True)
            50
        """
        try:
            logger.debug(f"Calculating trade certificate score (cert: {has_cert}, lang: {lang_ok})")
            
            if has_cert and lang_ok:
                return self.rules["certificate_of_qualification"]["with_official_language_proficiency"]
            return 0
                
        except Exception as e:
            logger.error(f"Error calculating trade certificate score: {e}")
            raise