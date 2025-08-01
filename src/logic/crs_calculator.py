import logging
import os
import sys
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass, field
from datetime import datetime

# Setup base project path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to resolve project root: %s", e)
    sys.exit(1)

from src.infra import setup_logging
from src.enums.value_enums import EducationLevel,MaritalStatus,CanadianEducationCategory
from src.immigration_rules import (get_age_factors,get_education_factors,get_work_experience_factors,get_first_language_factors,get_second_language_factors,
                                   get_spouse_education_factors,get_spouse_language_factors,get_spouse_work_experience_factors,
                                   get_additional_points_factors,get_canadian_work_education_points,get_certificate_of_qualification_points,get_foreign_canadian_combo_points,get_foreign_work_language_points,get_language_education_points,calculate_additional_points)



logger = setup_logging(name="CRS calculator")


@dataclass
class CoreFactors:
    """Core human capital factors for CRS calculation."""
    age: int = 0
    marital_status: MaritalStatus= MaritalStatus.SINGLE
    education_level: EducationLevel = EducationLevel.LESS_THAN_SECONDARY
    first_language_test_name:  Optional[str] = None
    first_language_scores: Optional[Dict[str, float]] = None
    second_language_test_name: Optional[str] = None
    second_language_scores: Optional[Dict[str, float]] = None
    canadain_work_experience_years: int = 0
    min_clb: int = 0
    second_clb : int =0
    canadian_citizen_spouse: bool = False
    spouse_come_with_you:bool =False
    


@dataclass
class SpouseFactors:
    """Spouse factors for CRS calculation."""
    education_level: Optional[EducationLevel] = None
    canadian_work_experience_years: int = 0
    language_test_name: Optional[str] = None
    language_scores: Optional[Dict[str, float]] = None
    min_clb: Optional[int] = None


@dataclass
class SkillTransferabilityFactors:
    """Skill transferability factors."""
    foreign_work_experience_years: int = 0
    has_certificate_of_qualification: bool = False
    # Detailed breakdown for reporting
    education: Optional[Dict[str, Any]] = None
    foreign_work_experience: Optional[Dict[str, Any]] = None
    certificate_of_qualification: int = 0


@dataclass
class AdditionalFactors:
    """Additional factors for CRS calculation."""
    arranged_employment: bool = False
    provincial_nomination: bool = False
    canadian_education: bool = False
    french_language_skills: bool = False
    canadian_sibling: bool = False


@dataclass
class CRSScores:
    """Container for all CRS scores."""
    core_human_capital: int = max(0, min(500, 0))
    spouse_factors: int = max(0, min(40, 0))
    skill_transferability: int = max(0, min(100, 0))
    additional_factors: int = max(0, min(600, 0))
    total: int = max(0, min(1200, 0)) #without PNP 600


    
class CRSCalculator:
    """
    Comprehensive CRS (Comprehensive Ranking System) Calculator for Canadian Express Entry.
    
    This calculator handles all four main sections:
    1. Core Human Capital Factors
    2. Spouse/Partner Factors
    3. Skill Transferability Factors
    4. Additional Factors
    """

    def __init__(self, marital_status: MaritalStatus, canadian_citizen_spouse: bool = False, spouse_come_with_you:bool =False):
        """
        Initialize the CRS Calculator with configuration and factor rules.
        
        Args:
            has_spouse: Whether the applicant has a spouse/partner
            canadian_citizen_spouse: Whether the spouse is a Canadian citizen
        """
        # Configuration
        self.has_spouse = self._has_spouse(marital_status=marital_status, canadian_citizen_spouse=canadian_citizen_spouse,spouse_come_with_you=spouse_come_with_you)
        self.canadian_citizen_spouse = canadian_citizen_spouse
        self.spouse_come_with_you= spouse_come_with_you
        
        # Data containers
        self.core_factors = CoreFactors()
        self.spouse_factors = SpouseFactors()
        self.skill_transferability = SkillTransferabilityFactors()
        self.additional_factors = AdditionalFactors()
        self.scores = CRSScores()
        
        # Load factor rules
        self.load_factor_rules()
        
        # Metadata
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        
        logger.info(f"CRS Calculator initialized with spouse: {self.has_spouse}")

    def load_factor_rules(self) -> None:
        """Load all factor rules and scoring tables."""
        try:
            # These would typically be loaded from configuration files or database
            self.age_factors = get_age_factors()
            self.education_factors = get_education_factors()
            self.first_language_factors = get_first_language_factors()
            self.second_language_factors = get_second_language_factors()
            self.work_experience_factors = get_work_experience_factors()
            
            # Spouse factors
            self.spouse_education_factors =get_spouse_education_factors()
            self.spouse_work_factors =get_spouse_work_experience_factors()
            self.spouse_language_factors = get_spouse_language_factors()
            
            # Skill transferability factors
            self.language_education_factors = get_language_education_points()
            self.canadian_work_education_factors = get_canadian_work_education_points()
            self.foreign_work_language_factors = get_foreign_work_language_points()
            self.foreign_canadian_work_factors = get_foreign_canadian_combo_points()
            self.certificate_qualification_factors = get_certificate_of_qualification_points()
            
            # Additional factors
            self.additional_factor_rules = get_additional_points_factors()
            
            logger.info("All factor rules loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load factor rules: {e}")
            raise RuntimeError("Factor rules loading failed") from e
        
    def _has_spouse(
    self,
    marital_status: MaritalStatus,
    canadian_citizen_spouse: bool = False,
    spouse_come_with_you: bool = False
        ) -> bool:
        """
        Strictly follows the pseudocode logic:
        - Only "Married" or "Common-Law" can potentially have a spouse
        - For those statuses, spouse must:
        a) Be coming with applicant (spouse_come_with_you == True)
        b) NOT be a Canadian citizen (canadian_citizen_spouse == False)
        """
        if marital_status in [MaritalStatus.MARRIED, MaritalStatus.COMMON_LAW]:
            if spouse_come_with_you and not canadian_citizen_spouse:
                return True  # Use "With Spouse" CRS grids
            else:
                return False  # Use "Without Spouse" CRS grids
        else:  # Single, Divorced, Widowed, etc.
            return False  # Use "Without Spouse" CRS grids


    def calculate_core_human_capital(
        self,
        age: int,
        education_level: EducationLevel,
        first_language_test_name: str,
        first_language_scores: Dict[str, float],
        canadian_work_experience_years: int,
        second_language_test_name: Optional[str] = None,
        second_language_scores: Optional[Dict[str, float]] = None
    ) -> int:
        """
        Calculate Core Human Capital Factors (Section A).
        
        Args:
            age: Applicant's age
            education_level: Highest education level
            first_language_test_name: Name of first official language test
            first_language_scores: Test scores for first language
            work_experience_years: Years of work experience
            second_language_test_name: Name of second official language test (optional)
            second_language_scores: Test scores for second language (optional)
            
        Returns:
            Total core human capital points
        """
        try:
            # Save core factors
            self.core_factors.age = age
            self.core_factors.education_level = education_level
            self.core_factors.first_language_test_name = first_language_test_name
            self.core_factors.first_language_scores = first_language_scores
            self.core_factors.second_language_test_name = second_language_test_name
            self.core_factors.second_language_scores = second_language_scores
            self.core_factors.canadain_work_experience_years = canadian_work_experience_years

            total_points = 0

            # Calculate individual components
            age_points = self._calculate_age_points(age)
            education_points = self._calculate_education_points(education_level)
            first_lang_points, min_clb = self._calculate_first_language_points(
                first_language_test_name, first_language_scores
            )
            work_points = self._calculate_work_experience_points(canadian_work_experience_years)
            
            # Save min CLB for transferability calculations
            self.core_factors.min_clb = min_clb

            total_points = age_points + education_points + first_lang_points + work_points

            # Add second language points if provided
            if second_language_test_name and second_language_scores:
                second_lang_points, second_clb = self._calculate_second_language_points(
                    second_language_test_name, second_language_scores
                )
                 # Save second min CLB for transferability calculations
                self.core_factors.second_clb = second_clb
                total_points += second_lang_points

            self.scores.core_human_capital = total_points
            self._update_total_score()
            
            logger.info(f"Core human capital calculated: {total_points} points")
            return total_points

        except Exception as e:
            logger.error(f"Core human capital calculation failed: {e}")
            raise RuntimeError("Core calculation failed") from e

    def calculate_spouse_partner_factors(
        self,
        education_level: EducationLevel,
        canadian_work_experience_years: int,
        language_test_name: str,
        language_scores: Dict[str, float]
    ) -> int:
        """
        Calculate Spouse/Partner Factors (Section B).
        
        Args:
            education_level: Spouse's education level
            work_experience_years: Spouse's work experience years
            language_test_name: Spouse's language test name
            language_scores: Spouse's language test scores
            
        Returns:
            Total spouse/partner points
        """
        if not self.has_spouse or self.canadian_citizen_spouse:
            logger.info("No spouse points calculation needed")
            return 0

        try:
            # Save spouse factors
            self.spouse_factors.education_level = education_level
            self.spouse_factors.canadian_work_experience_years = canadian_work_experience_years
            self.spouse_factors.language_test_name = language_test_name
            self.spouse_factors.language_scores = language_scores

            total_points = 0

            # Calculate spouse components
            education_points = self._calculate_spouse_education_points(education_level)
            work_points = self._calculate_spouse_work_points(canadian_work_experience_years)
            language_points, spouse_min_clb = self._calculate_spouse_language_points(
                language_test_name, language_scores
            )
            
            # Save spouse min CLB
            self.spouse_factors.min_clb = spouse_min_clb

            total_points = education_points + work_points + language_points
            
            self.scores.spouse_factors = total_points
            self._update_total_score()
            
            logger.info(f"Spouse/partner factors calculated: {total_points} points")
            return total_points

        except Exception as e:
            logger.error(f"Spouse factors calculation failed: {e}")
            raise RuntimeError("Spouse calculation failed") from e

    def calculate_skill_transferability_factors(
        self,
        foreign_work_experience_years: int = 0,
        has_certificate_of_qualification: bool = False
        ) -> int:
        """
        Calculate Skill Transferability Factors (Section C).
        
        Based on official CRS criteria:
        - Education factors: maximum 50 points (choose best of language+education OR work+education)
        - Foreign work experience factors: maximum 50 points (choose best of language+foreign OR canadian+foreign)
        - Certificate of qualification: maximum 50 points
        - Overall maximum: 100 points total
        
        Args:
            foreign_work_experience_years: Years of foreign work experience
            has_certificate_of_qualification: Whether applicant has certificate of qualification
            
        Returns:
            Total skill transferability points (maximum 100)
        """
        try:
            # Save transferability factors
            self.skill_transferability.foreign_work_experience_years = foreign_work_experience_years
            self.skill_transferability.has_certificate_of_qualification = has_certificate_of_qualification
            
            # EDUCATION FACTORS (Maximum 50 points)
            # Choose the HIGHER of language+education OR canadian work+education
            language_education_points = self._calculate_language_education_transferability()
            canadian_work_education_points = self._calculate_canadian_work_education_transferability(
                self.core_factors.canadain_work_experience_years
            )
            
            # Take the maximum of the two education combinations (not both)
            education_factor_points = language_education_points + canadian_work_education_points
            if education_factor_points > 50:
                education_factor_points = 50
            
            logger.info(f"Education factors: Lang+Edu={language_education_points}, Work+Edu={canadian_work_education_points}, Taking max={education_factor_points}")
            
            # FOREIGN WORK EXPERIENCE FACTORS (Maximum 50 points)
            # Choose the HIGHER of language+foreign work OR canadian+foreign work
            foreign_work_language_points = self._calculate_foreign_work_language_transferability(
                foreig_yesrs=foreign_work_experience_years
            )
            foreign_canadian_work_points = self._calculate_foreign_canadian_work_transferability(
                foreign_work_experience_years
            )
            
            # Take the maximum of the two foreign work combinations (not both)
            foreign_work_factor_points = foreign_work_language_points+ foreign_canadian_work_points
            if foreign_work_factor_points > 50:
                foreign_work_factor_points = 50
            
            logger.info(f"Foreign work factors: Lang+Foreign={foreign_work_language_points}, Canadian+Foreign={foreign_canadian_work_points}, Taking max={foreign_work_factor_points}")
            
            # CERTIFICATE OF QUALIFICATION (Maximum 50 points)
            certificate_points = 0
            if has_certificate_of_qualification:
                certificate_points = self._calculate_certificate_qualification_transferability()
                certificate_points = min(certificate_points, 50)  # Cap at 50
                logger.info(f"Certificate qualification points: {certificate_points}")
            
            # TOTAL CALCULATION
            # Add all factor categories together
            subtotal = education_factor_points + foreign_work_factor_points + certificate_points
            
            # Apply overall maximum of 100 points
            total_points = min(subtotal, 100)
            
            logger.info(f"Skill transferability breakdown: Education={education_factor_points}, Foreign Work={foreign_work_factor_points}, Certificate={certificate_points}, Subtotal={subtotal}, Final={total_points}")
            
            # Update detailed breakdown for reporting
            self.skill_transferability.education = {
                'official_language_and_education': language_education_points,
                'canadian_work_experience_and_education': canadian_work_education_points,
                'subtotal': education_factor_points
            }
            
            self.skill_transferability.foreign_work_experience = {
                'official_language_and_foreign_work': foreign_work_language_points,
                'canadian_and_foreign_work': foreign_canadian_work_points,
                'subtotal': foreign_work_factor_points
            }
            
            self.skill_transferability.certificate_of_qualification = certificate_points
            
            self.scores.skill_transferability = total_points
            self._update_total_score()
            
            logger.info(f"Skill transferability calculated: {total_points} points")
            return total_points
            
        except Exception as e:
            logger.error(f"Skill transferability calculation failed: {e}")
            raise RuntimeError("Transferability calculation failed") from e

    def determine_canadian_education_category(
        self,
        has_canadian_education: bool,
        canadian_education_type: str
        ) -> tuple[CanadianEducationCategory, int]:
        """
        Determine Canadian education category - cleaner version with exact mapping.
        """
        
        if not has_canadian_education:
            return CanadianEducationCategory.NONE, 0
        
        # Clean the input
        education_type = canadian_education_type.lower().strip()
        
        # Exact mapping based on your form values
        if education_type == 'secondary_or_less':
            return CanadianEducationCategory.SECONDARY_OR_LESS, 0
        
        elif education_type == 'one_or_two_diploma':
            return CanadianEducationCategory.ONE_TWO_YEAR, 2
        
        elif education_type == 'degree_three_years_or_more':
            return CanadianEducationCategory.THREE_PLUS_OR_ADVANCED, 3
        
        else:
            # Log unrecognized value for debugging
            logger.error(f"Unrecognized Canadian education type: '{canadian_education_type}'")
            logger.warning("Expected one of: 'secondary_or_less', 'one_or_two_diploma', 'degree_three_years_or_more'")
            return CanadianEducationCategory.NONE, 0

    # Updated calculate_additional_factors method for your CRS calculator
    def calculate_additional_factors(
        self,
        has_sibling_in_canada: bool = False,
        has_provincial_nomination: bool = False,
        # Canadian education parameters
        has_canadian_education: bool = False,
        canadian_education_type: str = ""
    ) -> int:
        """
        Calculate Additional Factors (Section D) with Canadian education category detection.
        
        Args:
            has_sibling_in_canada: Has Canadian citizen/PR sibling
            has_provincial_nomination: Has provincial nomination
            has_canadian_education: Boolean - has Canadian degree/diploma/certificate
            canadian_education_type: String from dropdown selection:
                - "Secondary (high school) or less"
                - "One- or two-year diploma or certificate"
                - "Degree, diploma or certificate of three years or longer OR a Master's, professional or doctoral degree"
            
        Returns:
            Total additional factor points
        """
        try:
            # Save additional factors
            self.additional_factors.canadian_sibling = has_sibling_in_canada
            self.additional_factors.provincial_nomination = has_provincial_nomination
            self.additional_factors.canadian_education = has_canadian_education

            # Determine Canadian education category and years
            education_category, canadian_education_years = self.determine_canadian_education_category(
                has_canadian_education, canadian_education_type
            )
            
            logger.info(f"Canadian education: {education_category.value} -> {canadian_education_years} years for CRS")

            # Prepare language test data from core factors (your existing code)
            first_test = None
            second_test = None
            
            if self.core_factors.first_language_test_name and self.core_factors.min_clb:
                from src.enums.value_enums import LanguageTestEnum
                try:
                    first_test_enum = LanguageTestEnum(self.core_factors.first_language_test_name.upper())
                except ValueError:
                    first_test_enum = getattr(LanguageTestEnum, self.core_factors.first_language_test_name.upper(), None)
                
                if first_test_enum:
                    first_test = {
                        'test_name': first_test_enum,
                        'clb_level': self.core_factors.min_clb
                    }
            
            if (self.core_factors.second_language_test_name and 
                self.core_factors.second_language_scores):
                second_lang_clb = self.core_factors.second_clb
                if second_lang_clb:
                    try:
                        second_test_enum = LanguageTestEnum(self.core_factors.second_language_test_name.upper())
                    except ValueError:
                        second_test_enum = getattr(LanguageTestEnum, self.core_factors.second_language_test_name.upper(), None)
                    
                    if second_test_enum:
                        second_test = {
                            'test_name': second_test_enum,
                            'clb_level': second_lang_clb
                        }

            # Use your existing calculation function
            total_points = calculate_additional_points(
                points_factors=self.additional_factor_rules,
                first_test=first_test or {'test_name': LanguageTestEnum.IELTS, 'clb_level': 0},
                second_test=second_test,
                has_sibling_in_canada=has_sibling_in_canada,
                has_provincial_nomination=has_provincial_nomination,
                canadian_education_years=canadian_education_years  # Now properly categorized
            )

            self.scores.additional_factors = total_points
            self._update_total_score()
            
            logger.info(f"Additional factors calculated: {total_points} points")
            return total_points

        except Exception as e:
            logger.error(f"Additional factors calculation failed: {e}")
            raise RuntimeError("Additional factors calculation failed") from e

    def get_total_crs_score(self) -> int:
        """
        Get the total CRS score.
        
        Returns:
            Total CRS score across all sections
        """
        return self.scores.total

    
    def _update_total_score(self) -> None:
        """Update the total CRS score."""
        self.scores.total = (
            self.scores.core_human_capital +
            self.scores.spouse_factors +
            self.scores.skill_transferability +
            self.scores.additional_factors
        )
        self.last_updated = datetime.now()

    # Helper methods for individual calculations
    def _calculate_age_points(self, age: int) -> int:
        """Calculate age points using immigration rules."""
        from src.immigration_rules import calculate_age_points
        return calculate_age_points(age, self.has_spouse, self.age_factors)

    def _calculate_education_points(self, education_level: EducationLevel) -> int:
        """Calculate education points using immigration rules."""
        from src.immigration_rules import calculate_education_points
        return calculate_education_points(education_level, self.has_spouse, self.education_factors)

    def _calculate_first_language_points(self, test_name: str, scores: Dict[str, float]) -> tuple[int, int]:
        """Calculate first language points and return min CLB."""
        from src.immigration_rules import calculate_language_points
        return calculate_language_points(test_name, scores, self.has_spouse, self.first_language_factors)

    def _calculate_second_language_points(self, test_name: str, scores: Dict[str, float]) -> tuple[int, int]:
        """Calculate second language points."""
        from src.immigration_rules import calculate_second_language_points
        return calculate_second_language_points(test_name, scores, self.has_spouse, self.second_language_factors)

    def _calculate_work_experience_points(self, years: int) -> int:
        """Calculate work experience points."""
        from src.immigration_rules import calculate_work_experience_points
        return calculate_work_experience_points(years, self.has_spouse, self.work_experience_factors)

    def _calculate_spouse_education_points(self, education_level: EducationLevel) -> int:
        """Calculate spouse education points."""
        from src.immigration_rules import calculate_spouse_education_points
        return calculate_spouse_education_points(education_level, True, self.spouse_education_factors)

    def _calculate_spouse_work_points(self, years: int) -> int:
        """Calculate spouse work experience points."""
        from src.immigration_rules import calculate_spouse_work_experience_points
        return calculate_spouse_work_experience_points(years, True, self.spouse_work_factors)

    def _calculate_spouse_language_points(self, test_name: str, scores: Dict[str, float]) -> tuple[int, int]:
        """Calculate spouse language points and return min CLB."""
        from src.immigration_rules import calculate_spouse_language_points
        return calculate_spouse_language_points(test_name, scores, True, self.spouse_language_factors)

    def _calculate_language_education_transferability(self) -> int:
        """Calculate language + education transferability points."""
        if not (self.core_factors.education_level and self.core_factors.min_clb):
            return 0
        from src.immigration_rules import calculate_language_education_points
        return calculate_language_education_points(
            self.core_factors.education_level,
            self.core_factors.min_clb,
            self.language_education_factors
        )

    def _calculate_canadian_work_education_transferability(self, canadian_years: int) -> int:
        """Calculate Canadian work + education transferability points."""
        if not (self.core_factors.education_level and canadian_years > 0):
            return 0
        from src.immigration_rules import calculate_canadian_work_education_points
        return calculate_canadian_work_education_points(
            self.core_factors.education_level,
            canadian_years,
            self.canadian_work_education_factors
        )

    def _calculate_foreign_work_language_transferability(self, foreig_yesrs: int) -> int:
        """Calculate foreign work + language transferability points."""
        if not (self.core_factors.canadain_work_experience_years and self.core_factors.min_clb):
            return 0
        from src.immigration_rules import calculate_foreign_work_language_points
        return calculate_foreign_work_language_points(
            foreig_yesrs,
            self.core_factors.min_clb,
            self.foreign_work_language_factors
        )

    def _calculate_foreign_canadian_work_transferability(self, foreig_yesrs: int) -> int:
        """Calculate foreign work + Canadian work transferability points."""
        if not (self.core_factors.canadain_work_experience_years and foreig_yesrs > 0):
            return 0
        from src.immigration_rules import calculate_foreign_canadian_work_points
        return calculate_foreign_canadian_work_points(
            foreig_yesrs,
            self.core_factors.canadain_work_experience_years,
            self.foreign_canadian_work_factors
        )

    def _calculate_certificate_qualification_transferability(self) -> int:
        """Calculate certificate of qualification transferability points."""
        if not self.core_factors.min_clb:
            return 0
        from src.immigration_rules import calculate_certificate_of_qualification_points
        return calculate_certificate_of_qualification_points(
            self.core_factors.min_clb,
            self.certificate_qualification_factors
        )
def calculate_comprehensive_crs_score(
        # Personal Information
        age: int,
        marital_status: MaritalStatus,
        education_level: EducationLevel,
        
        # Language Test Information
        first_language_test_name: str,
        first_language_scores: Dict[str, float],
        second_language_test_name: Optional[str] = None,
        second_language_scores: Optional[Dict[str, float]] = None,
        
        # Work Experience
        canadian_work_experience_years: int = 0,
        foreign_work_experience_years: int = 0,
        
        # Spouse Information (if applicable)
        canadian_citizen_spouse: bool = False,
        spouse_come_with_you: bool = False,
        spouse_education_level: Optional[EducationLevel] = None,
        spouse_canadian_work_experience_years: int = 0,
        spouse_language_test_name: Optional[str] = None,
        spouse_language_scores: Optional[Dict[str, float]] = None,
        
        # Skill Transferability Factors
        has_certificate_of_qualification: bool = False,
        
        # Additional Factors
        has_sibling_in_canada: bool = False,
        has_provincial_nomination: bool = False,
        has_canadian_education: bool = False,
        canadian_education_type: str = "",
        
        ) -> CRSScores:
        """
        Calculate comprehensive CRS score for Canadian Express Entry application.
        
        This function handles all four main CRS components:
        1. Core Human Capital Factors (max 500 points)
        2. Spouse/Partner Factors (max 40 points) 
        3. Skill Transferability Factors (max 100 points)
        4. Additional Factors (max 600 points)
        
        Args:
            age (int): Applicant's age in years
            marital_status (MaritalStatus): Current marital status
            education_level (EducationLevel): Highest level of education completed
            
            first_language_test_name (str): Name of first official language test
                (e.g., "IELTS", "CELPIP", "TEF", "TCF")
            first_language_scores (Dict[str, float]): Test scores by skill
                Format: {"listening": score, "reading": score, "writing": score, "speaking": score}
            second_language_test_name (Optional[str]): Name of second language test
            second_language_scores (Optional[Dict[str, float]]): Second language test scores
            
            canadian_work_experience_years (int): Years of Canadian work experience
            foreign_work_experience_years (int): Years of foreign work experience
            
            canadian_citizen_spouse (bool): True if spouse is Canadian citizen/PR
            spouse_come_with_you (bool): True if spouse will accompany to Canada
            spouse_education_level (Optional[EducationLevel]): Spouse's education level
            spouse_canadian_work_experience_years (int): Spouse's Canadian work experience
            spouse_language_test_name (Optional[str]): Spouse's language test name
            spouse_language_scores (Optional[Dict[str, float]]): Spouse's language scores
            
            has_certificate_of_qualification (bool): Has certificate of qualification
            
            has_sibling_in_canada (bool): Has Canadian citizen/PR sibling
            has_provincial_nomination (bool): Has provincial nomination
            has_canadian_education (bool): Has Canadian education credentials
            canadian_education_type (str): Type of Canadian education if applicable
                Options: "Secondary (high school) or less",
                        "One- or two-year diploma or certificate",
                        "Degree, diploma or certificate of three years or longer OR a Master's, professional or doctoral degree"
        
        Returns:
            CRSResult: Object containing all four CRS component scores and total
        
        Raises:
            ValueError: If required parameters are missing or invalid
            RuntimeError: If calculation fails due to system error
        
        Example:
            >>> result = calculate_comprehensive_crs_score(
            ...     age=29,
            ...     marital_status=MaritalStatus.SINGLE,
            ...     education_level=EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE,
            ...     first_language_test_name="IELTS",
            ...     first_language_scores={"listening": 8.0, "reading": 7.5, "writing": 7.0, "speaking": 7.5},
            ...     canadian_work_experience_years=2,
            ...     foreign_work_experience_years=3
            ... )
            >>> print(f"Total CRS Score: {result.total_score}")
        """
        
        # Input validation
        if age < 18 or age > 65:
            raise ValueError("Age must be between 18 and 65")
        
        if not first_language_test_name or not first_language_scores:
            raise ValueError("First language test name and scores are required")
        
        required_skills = {"listening", "reading", "writing", "speaking"}
        if not required_skills.issubset(first_language_scores.keys()):
            raise ValueError(f"First language scores must include: {required_skills}")
        
        try:
            # Initialize CRS calculator with marital status configuration
            calculator = CRSCalculator(
                marital_status=marital_status,
                canadian_citizen_spouse=canadian_citizen_spouse,
                spouse_come_with_you=spouse_come_with_you
            )
            
            # 1. Calculate Core Human Capital Factors (Section A)
            core_score = calculator.calculate_core_human_capital(
                age=age,
                education_level=education_level,
                first_language_test_name=first_language_test_name,
                first_language_scores=first_language_scores,
                canadian_work_experience_years=canadian_work_experience_years,
                second_language_test_name=second_language_test_name,
                second_language_scores=second_language_scores
            )
            
            # 2. Calculate Spouse/Partner Factors (Section B)
            spouse_score = 0
            if (calculator.has_spouse and 
                spouse_education_level and 
                spouse_language_test_name and 
                spouse_language_scores):
                
                spouse_score = calculator.calculate_spouse_partner_factors(
                    education_level=spouse_education_level,
                    canadian_work_experience_years=spouse_canadian_work_experience_years,
                    language_test_name=spouse_language_test_name,
                    language_scores=spouse_language_scores
                )
            
            # 3. Calculate Skill Transferability Factors (Section C)
            skill_transferability_score = calculator.calculate_skill_transferability_factors(
                foreign_work_experience_years=foreign_work_experience_years,
                has_certificate_of_qualification=has_certificate_of_qualification
            )
            
            # 4. Calculate Additional Factors (Section D)
            additional_factors_score = calculator.calculate_additional_factors(
                has_sibling_in_canada=has_sibling_in_canada,
                has_provincial_nomination=has_provincial_nomination,
                has_canadian_education=has_canadian_education,
                canadian_education_type=canadian_education_type
            )
            
            # Get total score from calculator
            total_score = calculator.get_total_crs_score()
            
            # Return comprehensive results
            return CRSScores(
                core_human_capital=core_score,
                skill_transferability=skill_transferability_score,
                additional_factors=additional_factors_score,
                total=total_score,
                spouse_factors=spouse_score
            )
            
        except Exception as e:
            raise RuntimeError(f"CRS calculation failed: {str(e)}") from e


def print_crs_breakdown(result: CRSScores) -> None:
        """
        Print a formatted breakdown of CRS scores.
        
        Args:
            result (CRSResult): CRS calculation result object
        """
        print("\n" + "="*50)
        print("CRS SCORE BREAKDOWN")
        print("="*50)
        print(f"Core Human Capital Factors:     {result.core_human_capital:3d}/500")
        print(f"Spouse/Partner Factors:         {result.spouse_factors:3d}/40")
        print(f"Skill Transferability Factors:  {result.skill_transferability:3d}/100")
        print(f"Additional Factors:             {result.additional_factors:3d}/600")
        print("-"*50)
        print(f"TOTAL CRS SCORE:                {result.total:3d}/1200")
        print("="*50)


def print_example_header(example_num, description):
    print(f"\n{'='*50}")
    print(f"EXAMPLE {example_num}: {description}")
    print(f"{'='*50}")



if __name__ == "__main__":
    # Example 1: Married couple with strong language scores
    print_example_header(1, "Married Couple with Strong Profile")
    calculator = CRSCalculator(
        marital_status=MaritalStatus.MARRIED,
        canadian_citizen_spouse=False,
        spouse_come_with_you=True
    )
    
    core_points = calculator.calculate_core_human_capital(
        age=28,
        education_level=EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE,
        first_language_test_name="IELTS",
        first_language_scores={"listening": 8.0, "reading": 8.0, "writing": 7.0, "speaking": 7.5},
        canadian_work_experience_years=3
    )
    
    spouse_points = calculator.calculate_spouse_partner_factors(
        education_level=EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE,
        canadian_work_experience_years=2,
        language_test_name="IELTS",
        language_scores={"listening": 7.5, "reading": 6.5, "writing": 6.5, "speaking": 7.0}
    )
    
    transfer_points = calculator.calculate_skill_transferability_factors(
        foreign_work_experience_years=2,
        has_certificate_of_qualification=False
    )
    
    additional_points = calculator.calculate_additional_factors(
        has_sibling_in_canada=True,
        has_canadian_education=True,
        canadian_education_type="One- or two-year diploma or certificate",
        has_provincial_nomination=False
    )
    
    print_crs_breakdown(calculator.scores)

    # Example 2: Single applicant with perfect language scores
    print_example_header(2, "Single Applicant with Perfect CELPIP Scores")
    calculator = CRSCalculator(marital_status=MaritalStatus.SINGLE)

    calculator.calculate_core_human_capital(
        age=31,
        education_level=EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE,
        first_language_test_name="CELPIP",
        first_language_scores={"listening": 10, "reading": 10, "writing": 9, "speaking": 9},
        canadian_work_experience_years=4
    )

    calculator.calculate_skill_transferability_factors(
        foreign_work_experience_years=5,
        has_certificate_of_qualification=True
    )

    calculator.calculate_additional_factors(
        has_sibling_in_canada=False,
        has_canadian_education=False
    )

    print_crs_breakdown(calculator.scores)

    # Example 3: Married to Canadian citizen (no spouse points)
    print_example_header(3, "Applicant Married to Canadian Citizen")
    calculator = CRSCalculator(
        marital_status=MaritalStatus.MARRIED,
        canadian_citizen_spouse=True,
        spouse_come_with_you=False
    )

    calculator.calculate_core_human_capital(
        age=29,
        education_level=EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE,
        first_language_test_name="IELTS",
        first_language_scores={"listening": 7.5, "reading": 8.0, "writing": 7.0, "speaking": 7.5},
        canadian_work_experience_years=2
    )

    calculator.calculate_skill_transferability_factors(
        foreign_work_experience_years=3,
        has_certificate_of_qualification=False
    )

    calculator.calculate_additional_factors(
        has_sibling_in_canada=True,
        has_canadian_education=True,
        canadian_education_type="Degree, diploma or certificate of three years or longer OR a Master's, professional or doctoral degree"
    )

    print_crs_breakdown(calculator.scores)

    # Example 4: Provincial Nominee (600 bonus points)
    print_example_header(4, "Provincial Nominee Applicant")
    calculator = CRSCalculator(marital_status=MaritalStatus.SINGLE)

    calculator.calculate_core_human_capital(
        age=35,
        education_level=EducationLevel.TWO_YEAR_POST_SECONDARY,
        first_language_test_name="TEF",
        first_language_scores={"listening": 349, "reading": 297, "writing": 371, "speaking": 349},
        canadian_work_experience_years=1
    )

    calculator.calculate_skill_transferability_factors(
        foreign_work_experience_years=8,
        has_certificate_of_qualification=True
    )

    calculator.calculate_additional_factors(
        has_provincial_nomination=True,
        has_sibling_in_canada=False
    )

    print_crs_breakdown(calculator.scores)

    # Example 5: Young student with Canadian education
    print_example_header(5, "Young Applicant with Canadian Education")
    calculator = CRSCalculator(marital_status=MaritalStatus.SINGLE)

    calculator.calculate_core_human_capital(
        age=22,
        education_level=EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE,
        first_language_test_name="IELTS",
        first_language_scores={"listening": 6.5, "reading": 6.5, "writing": 6.0, "speaking": 6.5},
        canadian_work_experience_years=0
    )

    calculator.calculate_skill_transferability_factors()

    calculator.calculate_additional_factors(
        has_canadian_education=True,
        canadian_education_type="Degree, diploma or certificate of three years or longer OR a Master's, professional or doctoral degree",
        has_sibling_in_canada=True
    )

    print_crs_breakdown(calculator.scores)

    # Example 6: Older married couple with moderate scores
    print_example_header(6, "Older Married Couple with Moderate Profile")
    calculator = CRSCalculator(
        marital_status=MaritalStatus.MARRIED,
        canadian_citizen_spouse=False,
        spouse_come_with_you=True
    )

    calculator.calculate_core_human_capital(
        age=40,
        education_level=EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE,
        first_language_test_name="CELPIP",
        first_language_scores={"listening": 8, "reading": 8, "writing": 7, "speaking": 8},
        canadian_work_experience_years=2
    )

    calculator.calculate_spouse_partner_factors(
        education_level=EducationLevel.TWO_OR_MORE_CERTIFICATES,
        canadian_work_experience_years=1,
        language_test_name="CELPIP",
        language_scores={"listening": 7, "reading": 7, "writing": 6, "speaking": 7}
    )

    calculator.calculate_skill_transferability_factors(
        foreign_work_experience_years=10,
        has_certificate_of_qualification=False
    )

    calculator.calculate_additional_factors(
        has_sibling_in_canada=False,
        has_canadian_education=False
    )

    print_crs_breakdown(calculator.scores)

        # Example 7: Bilingual Applicant (French first, English second)
    print_example_header(7, "Bilingual Applicant with French as First Language and English as Second Language")
    calculator = CRSCalculator(
        marital_status=MaritalStatus.SINGLE,
        canadian_citizen_spouse=False,
        spouse_come_with_you=True
    )

    # Core factors with French as first language (TEF)
    core_points = calculator.calculate_core_human_capital(
        age=32,
        education_level=EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE,
        first_language_test_name="TEF",
        first_language_scores={"listening": 349, "reading": 297, "writing": 371, "speaking": 349},  # CLB 9 equivalent
        second_language_test_name="IELTS",
        second_language_scores={"listening": 7.5, "reading": 7.0, "writing": 6.5, "speaking": 7.0},  # CLB 8 equivalent
        canadian_work_experience_years=3
    )


    # Skill transferability
    transfer_points = calculator.calculate_skill_transferability_factors(
        foreign_work_experience_years=4,
        has_certificate_of_qualification=True
    )

    # Additional factors
    additional_points = calculator.calculate_additional_factors(
        has_canadian_education=True,
        canadian_education_type="Two-year post-secondary program",
        has_sibling_in_canada=False,
    )

    # Print detailed results
    print_crs_breakdown(calculator.scores)
