"""
immigration_rules/__init__.py

This module aggregates and exposes all rule-related models and loading functions
used in the immigration points evaluation system. Each imported class represents a
structured Pydantic model defining a specific category of rules (e.g., Age, Education, 
Language), and each loader function provides the ability to extract and validate 
these rules from JSON files.

The exposed interface via `__all__` ensures clean and explicit imports across 
modules, supporting modularity, readability, and ease of use within the system.

Exposed Components:
- Models: Pydantic classes describing rule schemas
- Loaders: Functions that parse JSON and return validated model instances
"""

from .canadian_work_exp_models import WorkExperienceFactors, get_work_experience_factors
from .foreign_canadian_work_models import ForeignCanadianWorkFactors, get_foreign_canadian_combo_points
from .work_education_models import CanadianWorkEducationFactors, get_canadian_work_education_points
from .certificate_of_qualification_models import CertificateOfQualificationFactors, get_certificate_of_qualification_points
from .foreign_work_language_models import ForeignWorkLanguageCombinationFactors, get_foreign_work_language_points
from .spouse_education_models import SpouseEducationFactors, get_spouse_education_factors
from .additional_point_models import AdditionalPointsFactors, get_additional_points_factors
from .education_models import EducationFactors, get_education_factors
from .language_education_models import LanguageEducationCombinationFactors, get_language_education_points
from .spouse_language_models import SpouseLanguageFactors, get_spouse_language_factors
from .age_models import AgeFactors, get_age_factors
from .first_language_models import FirstLanguageFactors, get_first_language_factors
from .second_language_models import SecondLanguageFactors, get_second_language_factors
from .spouse_work_models import SpouseWorkExperienceFactors, get_spouse_work_experience_factors

__all__ = [
    # Models
    "WorkExperienceFactors",
    "ForeignCanadianWorkFactors",
    "CanadianWorkEducationFactors",
    "CertificateOfQualificationFactors",
    "ForeignWorkLanguageCombinationFactors",
    "SpouseEducationFactors",
    "AdditionalPointsFactors",
    "EducationFactors",
    "LanguageEducationCombinationFactors",
    "SpouseLanguageFactors",
    "AgeFactors",
    "FirstLanguageFactors",
    "SecondLanguageFactors",
    "SpouseWorkExperienceFactors",

    # Loaders
    "get_work_experience_factors",
    "get_foreign_canadian_combo_points",
    "get_canadian_work_education_points",
    "get_certificate_of_qualification_points",
    "get_foreign_work_language_points",
    "get_spouse_education_factors",
    "get_additional_points_factors",
    "get_education_factors",
    "get_language_education_points",
    "get_spouse_language_factors",
    "get_age_factors",
    "get_first_language_factors",
    "get_second_language_factors",
    "get_spouse_work_experience_factors",
]
