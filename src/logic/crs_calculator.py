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
        Determine Canadian education category and corresponding years for CRS calculation.
        
        Args:
            has_canadian_education: Boolean - does the person have Canadian education?
            canadian_education_type: String matching the dropdown options:
                - "Secondary (high school) or less"
                - "One- or two-year diploma or certificate"  
                - "Degree, diploma or certificate of three years or longer OR a Master's, professional or doctoral degree"
        
        Returns:
            Tuple of (CanadianEducationCategory, years_for_crs_calculation)
        """
        
        if not has_canadian_education:
            return CanadianEducationCategory.NONE, 0
        
        # Normalize the input string for matching
        education_type_lower = canadian_education_type.lower().strip()
        
        # Map dropdown selections to categories and years
        if any(term in education_type_lower for term in ["secondary", "high school", "less"]):
            return CanadianEducationCategory.SECONDARY_OR_LESS, 0
            
        elif any(term in education_type_lower for term in ["one-", "two-year", "one or two"]):
            return CanadianEducationCategory.ONE_TWO_YEAR, 2  # Use 2 as representative
            
        elif any(term in education_type_lower for term in ["three years", "longer", "master", "professional", "doctoral"]):
            return CanadianEducationCategory.THREE_PLUS_OR_ADVANCED, 3  # Use 3+ as representative
            
        else:
            # Default fallback
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

    def get_detailed_breakdown(self) -> Dict[str, Any]:
        """
        Get detailed score breakdown for Express Entry CRS.
        
        Returns:
            Dictionary containing detailed CRS breakdown with all saved values.
        """
        
        # Helper function to safely calculate individual points
        def calculate_individual_points():
            individual_points = {}
            
            try:
                # Age points
                if hasattr(self, '_calculate_age_points') and self.core_factors.age:
                    individual_points['age_points'] = self._calculate_age_points(self.core_factors.age)
                
                # Education points  
                if hasattr(self, '_calculate_education_points') and self.core_factors.education_level:
                    individual_points['education_points'] = self._calculate_education_points(self.core_factors.education_level)
                
                # First language points
                if (hasattr(self, '_calculate_first_language_points') and 
                    self.core_factors.first_language_test_name and 
                    self.core_factors.first_language_scores):
                    points, _ = self._calculate_first_language_points(
                        self.core_factors.first_language_test_name, 
                        self.core_factors.first_language_scores
                    )
                    individual_points['first_language_points'] = points
                
                # Second language points
                if (hasattr(self, '_calculate_second_language_points') and 
                    self.core_factors.second_language_test_name and 
                    self.core_factors.second_language_scores):
                    points, _ = self._calculate_second_language_points(
                        self.core_factors.second_language_test_name,
                        self.core_factors.second_language_scores
                    )
                    individual_points['second_language_points'] = points
                else:
                    individual_points['second_language_points'] = 0
                    
                # Work experience points
                if hasattr(self, '_calculate_work_experience_points'):
                    individual_points['work_experience_points'] = self._calculate_work_experience_points(
                        self.core_factors.canadain_work_experience_years
                    )
                    
            except Exception as e:
                logger.warning(f"Could not calculate individual points: {e}")
                
            return individual_points
        
        # Calculate individual component points
        individual_points = calculate_individual_points()
        
        return {
            "total_score": getattr(self.scores, "total", 0),  # out of 1200
            "calculation_timestamp": getattr(self, "last_updated", None),
            "has_spouse": getattr(self, "has_spouse", False),
            
            # Core / Human Capital Factors
            "core_human_capital": {
                "age": {
                    "value": getattr(self.core_factors, "age", 0),
                    "points": individual_points.get('age_points', 0)
                },
                "level_of_education": {
                    "value": getattr(self.core_factors, "education_level", None),
                    "value_display": getattr(self.core_factors, "education_level", "").value if getattr(self.core_factors, "education_level", None) else "Not specified", # type: ignore
                    "points": individual_points.get('education_points', 0)
                },
                "official_languages": {
                    "first_official_language": {
                        "test_name": getattr(self.core_factors, "first_language_test_name", ""),
                        "scores": getattr(self.core_factors, "first_language_scores", {}),
                        "min_clb": getattr(self.core_factors, "min_clb", 0),
                        "points": individual_points.get('first_language_points', 0)
                    },
                    "second_official_language": {
                        "test_name": getattr(self.core_factors, "second_language_test_name", ""),
                        "scores": getattr(self.core_factors, "second_language_scores", {}),
                        "min_clb": getattr(self.core_factors, "second_clb", 0),
                        "points": individual_points.get('second_language_points', 0)
                    }
                },
                "canadian_work_experience": {
                    "years": getattr(self.core_factors, "canadain_work_experience_years", 0),
                    "points": individual_points.get('work_experience_points', 0)
                },
                "subtotal": getattr(self.scores, "core_human_capital", 0)
            },

            # Spouse Factors
            "spouse_factors": {
                "applicable": self.has_spouse and not self.canadian_citizen_spouse,
                "level_of_education": {
                    "value": getattr(self.spouse_factors, "education_level", None),
                    "value_display": getattr(self.spouse_factors, "education_level", "").value if getattr(self.spouse_factors, "education_level", None) else "Not specified" # type: ignore
                },
                "first_official_language": {
                    "test_name": getattr(self.spouse_factors, "language_test_name", ""),
                    "scores": getattr(self.spouse_factors, "language_scores", {}),
                    "min_clb": getattr(self.spouse_factors, "min_clb", 0)
                },
                "canadian_work_experience": {
                    "years": getattr(self.spouse_factors, "canadian_work_experience_years", 0)
                },
                "subtotal": getattr(self.scores, "spouse_factors", 0)
            },

            # Skill Transferability Factors
            "skill_transferability": {
                "education": {
                    "official_language_and_education": getattr(self.skill_transferability.education, "official_language_and_education", 0) if self.skill_transferability.education else 0,
                    "canadian_work_experience_and_education": getattr(self.skill_transferability.education, "canadian_work_experience_and_education", 0) if self.skill_transferability.education else 0,
                    "subtotal": getattr(self.skill_transferability.education, "subtotal", 0) if self.skill_transferability.education else 0
                },
                "foreign_work_experience": {
                    "years": getattr(self.skill_transferability, "foreign_work_experience_years", 0),
                    "official_language_and_foreign_work": getattr(self.skill_transferability.foreign_work_experience, "official_language_and_foreign_work", 0) if self.skill_transferability.foreign_work_experience else 0,
                    "canadian_and_foreign_work": getattr(self.skill_transferability.foreign_work_experience, "canadian_and_foreign_work", 0) if self.skill_transferability.foreign_work_experience else 0,
                    "subtotal": getattr(self.skill_transferability.foreign_work_experience, "subtotal", 0) if self.skill_transferability.foreign_work_experience else 0
                },
                "certificate_of_qualification": {
                    "has_certificate": getattr(self.skill_transferability, "has_certificate_of_qualification", False),
                    "points": getattr(self.skill_transferability, "certificate_of_qualification", 0)
                },
                "subtotal": getattr(self.scores, "skill_transferability", 0)
            },

            # Additional Points
            "additional_factors": {
                "provincial_nomination": {
                    "value": getattr(self.additional_factors, "provincial_nomination", False),
                    "points": 600 if getattr(self.additional_factors, "provincial_nomination", False) else 0
                },
                "canadian_education": {
                    "value": getattr(self.additional_factors, "canadian_education", False),
                    "points": "calculated_in_total"  # Points are calculated based on education type
                },
                "sibling_in_canada": {
                    "value": getattr(self.additional_factors, "canadian_sibling", False),
                    "points": "calculated_in_total"  # Points are calculated in the additional points function
                },
                "french_language_skills": {
                    "value": getattr(self.additional_factors, "french_language_skills", False),
                    "points": "calculated_in_total"  # Points are calculated based on language test results
                },
                "arranged_employment": {
                    "value": getattr(self.additional_factors, "arranged_employment", False),
                    "points": "calculated_in_total"  # Points would be calculated if implemented
                },
                "subtotal": getattr(self.scores, "additional_factors", 0)
            },

            # Raw Data for Debugging/Reference
            "raw_data": {
                "core_factors": {
                    "age": getattr(self.core_factors, "age", 0),
                    "marital_status": getattr(self.core_factors, "marital_status", "").value if getattr(self.core_factors, "marital_status", None) else "Not specified", # type: ignore
                    "education_level": getattr(self.core_factors, "education_level", "").value if getattr(self.core_factors, "education_level", None) else "Not specified", # type: ignore
                    "first_language_test_name": getattr(self.core_factors, "first_language_test_name", ""),
                    "first_language_scores": getattr(self.core_factors, "first_language_scores", {}),
                    "second_language_test_name": getattr(self.core_factors, "second_language_test_name", ""),
                    "second_language_scores": getattr(self.core_factors, "second_language_scores", {}),
                    "canadain_work_experience_years": getattr(self.core_factors, "canadain_work_experience_years", 0),
                    "min_clb": getattr(self.core_factors, "min_clb", 0),
                    "second_clb": getattr(self.core_factors, "second_clb", 0),
                    "canadian_citizen_spouse": getattr(self.core_factors, "canadian_citizen_spouse", False),
                    "spouse_come_with_you": getattr(self.core_factors, "spouse_come_with_you", False)
                },
                "spouse_factors": {
                    "education_level": getattr(self.spouse_factors, "education_level", "").value if getattr(self.spouse_factors, "education_level", None) else None, # type: ignore
                    "canadian_work_experience_years": getattr(self.spouse_factors, "canadian_work_experience_years", 0),
                    "language_test_name": getattr(self.spouse_factors, "language_test_name", ""),
                    "language_scores": getattr(self.spouse_factors, "language_scores", {}),
                    "min_clb": getattr(self.spouse_factors, "min_clb", 0)
                },
                "skill_transferability": {
                    "foreign_work_experience_years": getattr(self.skill_transferability, "foreign_work_experience_years", 0),
                    "has_certificate_of_qualification": getattr(self.skill_transferability, "has_certificate_of_qualification", False),
                    "education_breakdown": getattr(self.skill_transferability, "education", {}),
                    "foreign_work_breakdown": getattr(self.skill_transferability, "foreign_work_experience", {}),
                    "certificate_points": getattr(self.skill_transferability, "certificate_of_qualification", 0)
                },
                "additional_factors": {
                    "arranged_employment": getattr(self.additional_factors, "arranged_employment", False),
                    "provincial_nomination": getattr(self.additional_factors, "provincial_nomination", False),
                    "canadian_education": getattr(self.additional_factors, "canadian_education", False),
                    "french_language_skills": getattr(self.additional_factors, "french_language_skills", False),
                    "canadian_sibling": getattr(self.additional_factors, "canadian_sibling", False)
                }
            },

            # Meta information
            "created_at": getattr(self, "created_at", None),
            "last_updated": getattr(self, "last_updated", None),
            "calculator_config": {
                "has_spouse": getattr(self, "has_spouse", False),
                "canadian_citizen_spouse": getattr(self, "canadian_citizen_spouse", False),
                "spouse_come_with_you": getattr(self, "spouse_come_with_you", False)
            }
        }


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




# Example usage
if __name__ == "__main__":
    from pprint import pprint
    # Initialize calculator
    calculator = CRSCalculator(
        marital_status=MaritalStatus.MARRIED,
        canadian_citizen_spouse=False,
        spouse_come_with_you=True
    )
    
    # Calculate core factors
    core_points = calculator.calculate_core_human_capital(
        age=28,
        education_level=EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE,
        first_language_test_name="IELTS",
        first_language_scores={"listening": 8.0, "reading": 8.0, "writing": 7.0, "speaking": 7.5},
        canadian_work_experience_years=3
    )
    
    # Calculate spouse factors
    spouse_points = calculator.calculate_spouse_partner_factors(
        education_level=EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE,
        canadian_work_experience_years=2,
        language_test_name="IELTS",
        language_scores={"listening": 7.5, "reading": 6.5, "writing": 6.5, "speaking": 7.0}
    )
    
    # Calculate transferability
    transfer_points = calculator.calculate_skill_transferability_factors(
        foreign_work_experience_years=2,
        has_certificate_of_qualification=False
    )
    
    # Calculate additional factors
    additional_points = calculator.calculate_additional_factors(
        has_sibling_in_canada=True,
        has_canadian_education=True,
        canadian_education_type="One- or two-year diploma or certificate",
        has_provincial_nomination=False
    )
    
    # Get results
    total_score = calculator.get_total_crs_score()
    breakdown = calculator.get_detailed_breakdown()
    
    print(f"Total CRS Score: {total_score}")
    pprint(f"Detailed Breakdown: {breakdown}")