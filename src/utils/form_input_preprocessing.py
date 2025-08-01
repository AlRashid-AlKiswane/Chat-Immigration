"""
CRS Processing Module

This module contains all data processing and transformation functions
for CRS (Comprehensive Ranking System) calculations. It handles the conversion
between assessment form data and CRS calculator parameters.

Author: Rama Amairy
Created: 2024
"""

import re
import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime
import os
import sys


# Set up project base directory
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.error("Failed to set up main directory path: %s", e)
    sys.exit(1)


from src.enums.value_enums import EducationLevel, MaritalStatus
from src.schema import AssessmentAnswers
from src.infra import setup_logging
from src.logic import CRSScores

# Setup module logger
logger = setup_logging(name="FORM-INPUT-PREPROCESSING")




def map_string_to_enum(value: Optional[str], enum_class, field_name: str):
    """
    Map string values to enum values with comprehensive error handling.
    
    This function attempts multiple mapping strategies:
    1. Direct enum value mapping
    2. Uppercase attribute mapping
    3. Fuzzy matching for common variations
    
    Args:
        value (Optional[str]): String value to map
        enum_class: Target enum class (e.g., MaritalStatus, EducationLevel)  
        field_name (str): Field name for error messages
        
    Returns:
        Corresponding enum value
        
    """
    if not value or value.strip() == "":
        raise ValueError(f"{field_name} is required and cannot be empty")
    
    # Clean the input value
    clean_value = value.strip()
    
    try:
        # Strategy 1: Direct mapping with original case
        return enum_class(clean_value)
    except ValueError:
        pass
    
    try:
        # Strategy 2: Uppercase mapping
        return enum_class(clean_value.upper())
    except ValueError:
        pass
    
    try:
        # Strategy 3: Attribute-based mapping
        return getattr(enum_class, clean_value.upper())
    except AttributeError:
        pass
    
    # Strategy 4: Fuzzy matching for common variations
    fuzzy_mappings = _get_fuzzy_mappings(enum_class)
    clean_lower = clean_value.lower()
    
    for pattern, enum_value in fuzzy_mappings.items():
        if pattern in clean_lower:
            logger.info(f"Fuzzy matched '{clean_value}' to {enum_value} for {field_name}")
            return enum_value
    
    # All strategies failed
    valid_values = [e.value for e in enum_class]
    raise ValueError(
        f"Invalid {field_name}: '{value}'. Valid options: {valid_values}"
    )


def _get_fuzzy_mappings(enum_class) -> Dict[str, Any]:
    """
    Get fuzzy mapping patterns for enum values based on the CRS website options.
    """
    fuzzy_mappings = {}

    # Marital Status fuzzy mappings
    if enum_class == MaritalStatus:
        fuzzy_mappings.update({
            'annulled marriage': MaritalStatus.ANNULLED,
            'common-law': MaritalStatus.COMMON_LAW,
            'common law': MaritalStatus.COMMON_LAW,
            'divorced': MaritalStatus.DIVORCED,
            'separated': MaritalStatus.DIVORCED,
            'legally separated': MaritalStatus.LEGALLY_SEPARATED,
            'married': MaritalStatus.MARRIED,
            'never married': MaritalStatus.SINGLE,
            'single': MaritalStatus.SINGLE,
            'widowed': MaritalStatus.WIDOWED,
        })

    # Education Level fuzzy mappings
    elif enum_class == EducationLevel:
        fuzzy_mappings.update({
            'none': EducationLevel.LESS_THAN_SECONDARY,
            'less than secondary': EducationLevel.LESS_THAN_SECONDARY,
            'secondary diploma': EducationLevel.SECONDARY_DIPLOMA,
            'high school': EducationLevel.SECONDARY_DIPLOMA,
            'one-year program': EducationLevel.ONE_YEAR_POST_SECONDARY,
            '1 year': EducationLevel.ONE_YEAR_POST_SECONDARY,
            'two-year program': EducationLevel.TWO_YEAR_POST_SECONDARY,
            '2 year': EducationLevel.TWO_YEAR_POST_SECONDARY,
            'bachelor': EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE,
            'three or more year program': EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE,
            '3 year': EducationLevel.BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE,
            'two or more certificates': EducationLevel.TWO_OR_MORE_CERTIFICATES,
            '2 or more': EducationLevel.TWO_OR_MORE_CERTIFICATES,
            'master': EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE,
            'professional degree': EducationLevel.MASTERS_OR_PROFESSIONAL_DEGREE,
            'phd': EducationLevel.PHD,
            'doctoral': EducationLevel.PHD,
        })

    return fuzzy_mappings


def parse_score_value(score_str: str) -> float:
    """
    Parse various score formats including ranges and single values.
    
    Handles:
    - Simple numbers: '8.5' -> 8.5
    - Ranges: '503-545' -> 524.0 (midpoint)
    - Single values in some tests: '90' -> 90.0
    
    Args:
        score_str (str): Score string to parse
        
    Returns:
        float: Parsed score value
        
    Raises:
        ValueError: If score format is invalid
    """
    if not score_str or score_str.strip() == "":
        raise ValueError("Score cannot be empty")
    
    score_clean = score_str.strip()
    
    # Handle range format (e.g., '503-545', '88-90')
    if '-' in score_clean:
        try:
            parts = score_clean.split('-')
            if len(parts) != 2:
                raise ValueError(f"Invalid range format: {score_clean}")
            
            min_score = float(parts[0].strip())
            max_score = float(parts[1].strip())
            
            # Return midpoint of range
            midpoint = (min_score + max_score) / 2
            logger.debug(f"Converted range '{score_clean}' to midpoint: {midpoint}")
            return midpoint
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Could not parse score range '{score_clean}': {str(e)}")
    
    # Handle single number format
    try:
        return float(score_clean)
    except ValueError as e:
        raise ValueError(f"Could not parse score '{score_clean}': {str(e)}")


def convert_language_scores(scores_dict: Dict[str, str]) -> Dict[str, float]:
    """
    Convert language score strings to floats with validation.
    Now handles both simple scores and score ranges.
    
    Args:
        scores_dict (Dict[str, str]): Dictionary with string score values
        
    Returns:
        Dict[str, float]: Dictionary with validated float score values
        
    Raises:
        ValueError: If conversion fails or scores are invalid
        
    Example:
        >>> # Simple scores (IELTS, CELPIP)
        >>> scores1 = convert_language_scores({
        ...     "listening": "8.0",
        ...     "reading": "11", 
        ...     "writing": "7.0",
        ...     "speaking": "7.5"
        ... })
        >>> 
        >>> # Range scores (TEF, TCF, PTE)
        >>> scores2 = convert_language_scores({
        ...     "listening": "503-545",
        ...     "reading": "434-461", 
        ...     "writing": "428-471",
        ...     "speaking": "456-493"
        ... })
    """
    if not scores_dict:
        raise ValueError("Language scores dictionary cannot be empty")
    
    converted_scores = {}
    required_skills = {'listening', 'reading', 'writing', 'speaking'}
    
    for skill, score_str in scores_dict.items():
        if score_str is None or score_str == "":
            continue
            
        try:
            score_float = parse_score_value(score_str)
            
            # More flexible validation - different tests have different ranges
            if score_float < 0:
                raise ValueError(f"Score cannot be negative for {skill}: {score_float}")
            
            # Log unusual ranges but don't fail (different tests have different scales)
            if score_float > 100:
                logger.info(f"High score detected for {skill}: {score_float} (possibly TEF/TCF scale)")
            elif score_float > 12 and score_float <= 20:
                logger.info(f"Score for {skill}: {score_float} (possibly TCF speaking/writing scale)")
            elif score_float > 20:
                logger.info(f"Score for {skill}: {score_float} (possibly PTE/TEF/TCF scale)")
            
            converted_scores[skill] = score_float
            
        except ValueError as e:
            raise ValueError(f"Invalid score for {skill}: '{score_str}'. {str(e)}")
    
    # Check if we have all required skills
    missing_skills = required_skills - set(converted_scores.keys())
    if missing_skills:
        logger.warning(f"Missing language skills: {missing_skills}")
    
    return converted_scores


def extract_language_scores(assessment_dict: dict, prefix: str) -> Optional[Dict[str, str]]:
    """
    Extract language scores for a specific test from assessment data.
    
    Args:
        assessment_dict (dict): Assessment data dictionary
        prefix (str): Prefix for score fields (e.g., 'first_language_scores', 'second_language_scores')
        
    Returns:
        Optional[Dict[str, str]]: Dictionary of language scores or None if no scores found
        
    Example:
        >>> scores = extract_language_scores(data, 'first_language_scores')
        >>> # Returns: {'listening': '8.0', 'reading': '7.5', ...}
    """
    scores = {}
    skills = ['listening', 'speaking', 'reading', 'writing']
    
    for skill in skills:
        key = f"{prefix}_{skill}"
        if key in assessment_dict and assessment_dict[key] is not None:
            # Clean the score value
            score_value = str(assessment_dict[key]).strip()
            if score_value:  # Only add non-empty scores
                scores[skill] = score_value
    
    logger.debug(f"Extracted {prefix} scores: {scores}")
    return scores if scores else None


def convert_yes_no_to_bool(value: Optional[str], default: bool = False) -> bool:
    """
    Convert 'yes'/'no' string values to boolean with flexible input handling.
    
    Args:
        value (Optional[str]): String value ('yes', 'no', 'true', 'false', etc.)
        default (bool): Default value if input is None or invalid
        
    Returns:
        bool: Boolean value
        
    Example:
        >>> convert_yes_no_to_bool("Yes")  # True
        >>> convert_yes_no_to_bool("NO")   # False  
        >>> convert_yes_no_to_bool(None)   # False (default)
    """
    if not value:
        return default
    
    value_clean = value.lower().strip()
    
    # Positive values
    if value_clean in ['yes', 'true', '1', 'on']:
        return True
    
    # Negative values  
    if value_clean in ['no', 'false', '0', 'off']:
        return False
    
    logger.warning(f"Ambiguous boolean value: '{value}', using default: {default}")
    return default


def convert_years_string_to_int(value: Optional[str]) -> int:
    """
    Convert years string to integer with intelligent parsing.
    
    Handles various formats:
    - "2 years", "3", "5 year experience"
    - "No experience", "None", "Zero"
    - "Less than 1 year" -> 0
    - "More than 10 years" -> 10
    
    Args:
        value (Optional[str]): String representation of years
        
    Returns:
        int: Number of years (0 if invalid/none)
        
    Example:
        >>> convert_years_string_to_int("3 years")      # 3
        >>> convert_years_string_to_int("No experience") # 0
        >>> convert_years_string_to_int("More than 10")  # 10
    """
    if not value:
        return 0
    
    value_clean = value.lower().strip()
    
    # Handle explicit zero cases
    zero_indicators = ['no', 'none', 'zero', 'nil', 'less than 1']
    if any(indicator in value_clean for indicator in zero_indicators):
        return 0
    
    # Extract numbers using regex
    numbers = re.findall(r'\d+', value_clean)
    
    if numbers:
        years = int(numbers[0])
        
        # Handle "more than X" cases - use the number as is
        if 'more than' in value_clean or 'over' in value_clean:
            logger.debug(f"Interpreted 'more than' case: {value} -> {years}")
        
        # Reasonable validation
        if years > 50:
            logger.warning(f"Unusually high years value: {years} from '{value}'")
            return min(years, 50)  # Cap at 50 years
        
        return years
    
    logger.warning(f"Could not parse years from: '{value}'")
    return 0


def transform_assessment_to_crs_params(assessment_data: AssessmentAnswers) -> Dict[str, Any]:
    """
    Transform AssessmentAnswers to parameters expected by CRS calculator.
    
    This is the main transformation function that orchestrates all data conversion
    and validation steps. It handles:
    - Basic parameter mapping
    - Enum conversions
    - Language score processing
    - Spouse information handling
    - Additional factors processing
    
    Args:
        assessment_data (AssessmentAnswers): Pydantic model with assessment answers
        
    Returns:
        Dict[str, Any]: Dictionary with parameters for CRS calculation
        
    Raises:
        ValueError: If required data is missing or invalid
        ValueError: If enum mapping fails
        
    Example:
        >>> params = transform_assessment_to_crs_params(assessment_data)
        >>> crs_result = calculate_comprehensive_crs_score(**params)
    """
    logger.info("Starting assessment data transformation for CRS calculation")
    
    try:
        assessment_dict = assessment_data.dict()
        
        # Initialize parameters dictionary
        params = {}
        
        # 1. BASIC PARAMETERS
        logger.debug("Processing basic parameters")
        params['age'] = assessment_dict.get('age')
        if not params['age'] or params['age'] < 18 or params['age'] > 65:
            raise ValueError(f"Invalid age: {params['age']}. Must be between 18 and 65.")
        
        params['canadian_work_experience_years'] = convert_years_string_to_int(
            assessment_dict.get('canadian_work_experience')
        )
        params['foreign_work_experience_years'] = convert_years_string_to_int(
            assessment_dict.get('foreign_work_experience')
        )
        
        # 2. ENUM MAPPINGS
        logger.debug("Processing enum mappings")
        try:
            params['marital_status'] = map_string_to_enum(
                assessment_dict.get('marital_status'), 
                MaritalStatus, 
                'marital_status'
            )
            params['education_level'] = map_string_to_enum(
                assessment_dict.get('education_level'), 
                EducationLevel, 
                'education_level'
            )
        except ValueError as e:
            raise ValueError(f"Enum mapping failed: {str(e)}")
        
        # 3. LANGUAGE PROCESSING
        logger.debug("Processing language information")
        params['first_language_test_name'] = assessment_dict.get('first_language_test')
        if not params['first_language_test_name']:
            raise ValueError("First language test name is required")
        
        # First language scores (required)
        first_scores = extract_language_scores(assessment_dict, 'first_language_scores')
        if not first_scores:
            raise ValueError("First language scores are required")
        
        params['first_language_scores'] = convert_language_scores(first_scores)
        
        # Second language (optional)
        if assessment_dict.get('second_language_test'):
            params['second_language_test_name'] = assessment_dict.get('second_language_test')
            second_scores = extract_language_scores(assessment_dict, 'second_language_scores')
            if second_scores:
                params['second_language_scores'] = convert_language_scores(second_scores)
                logger.debug("Second language scores processed successfully")
        
        # 4. SPOUSE INFORMATION
        logger.debug("Processing spouse information")
        params['canadian_citizen_spouse'] = convert_yes_no_to_bool(
            assessment_dict.get('spouse_citizen')
        )
        params['spouse_come_with_you'] = convert_yes_no_to_bool(
            assessment_dict.get('spouse_coming')
        )
        
        # Spouse details (only if spouse is coming and not Canadian citizen)
        if params['spouse_come_with_you'] and not params['canadian_citizen_spouse']:
            logger.debug("Processing spouse details")
            
            if assessment_dict.get('spouse_education'):
                try:
                    params['spouse_education_level'] = map_string_to_enum(
                        assessment_dict.get('spouse_education'),
                        EducationLevel,
                        'spouse_education'
                    )
                except ValueError as e:
                    logger.warning(f"Spouse education mapping failed: {e}")
            
            params['spouse_canadian_work_experience_years'] = convert_years_string_to_int(
                assessment_dict.get('spouse_experience')
            )
            
            if assessment_dict.get('spouse_language_test'):
                params['spouse_language_test_name'] = assessment_dict.get('spouse_language_test')
                spouse_scores = extract_language_scores(assessment_dict, 'spouse_language_scores')
                if spouse_scores:
                    try:
                        params['spouse_language_scores'] = convert_language_scores(spouse_scores)
                        logger.debug("Spouse language scores processed successfully")
                    except ValueError as e:
                        logger.warning(f"Spouse language scores processing failed: {e}")
        
        # 5. ADDITIONAL FACTORS
        logger.debug("Processing additional factors")
        params['has_certificate_of_qualification'] = convert_yes_no_to_bool(
            assessment_dict.get('trade_certificate')
        )
        params['has_sibling_in_canada'] = convert_yes_no_to_bool(
            assessment_dict.get('siblings')
        )
        params['has_provincial_nomination'] = convert_yes_no_to_bool(
            assessment_dict.get('do_have_nomination')
        )
        params['has_canadian_education'] = convert_yes_no_to_bool(
            assessment_dict.get('canada_education')
        )
        
        # Canadian education type
        if params['has_canadian_education']:
            params['canadian_education_type'] = assessment_dict.get('education_eca', '')
            logger.debug(f"Canadian education type: {params['canadian_education_type']}")
        
        logger.info("Assessment data transformation completed successfully")
        logger.debug(f"Transformed parameters: {list(params.keys())}")
        
        return params
        
    except Exception as e:
        logger.error(f"Assessment transformation failed: {str(e)}")
        if isinstance(e, ValueError):
            raise
        else:
            raise ValueError(f"Unexpected error during transformation: {str(e)}")


def create_crs_response_data(
    crs_result: CRSScores, 
    user_name: str, 
    include_metadata: bool = True
) -> Dict[str, Any]:
    """
    Create standardized CRS response data structure.
    
    Args:
        crs_result (CRSResult): CRS calculation results
        user_name (str): Username for the calculation
        include_metadata (bool): Whether to include metadata like timestamp
        
    Returns:
        Dict[str, Any]: Standardized response data
        
    Example:
        >>> response_data = create_crs_response_data(crs_result, "john_doe")
        >>> print(response_data["total_crs_score"])
    """
    response_data = {
        "total_crs_score": crs_result.total,
        "breakdown": {
            "core_human_capital": crs_result.core_human_capital,
            "spouse_partner_factors": crs_result.spouse_factors,
            "skill_transferability": crs_result.skill_transferability,
            "additional_factors": crs_result.additional_factors
        },
        "user_name": user_name
    }
    
    if include_metadata:
        response_data["calculated_at"] = datetime.now().isoformat()
        response_data["calculation_version"] = "1.0"
    
    return response_data