from pydantic import BaseModel, Field
from typing import Optional


class SpouseWorkExperienceWithSpouse(BaseModel):
    """
    Spouse's Canadian work experience points calculation for applicants with a spouse or common-law partner.
    Maximum 10 points.
    """
    
    none_or_less_than_year: int = Field(
        0,
        description="None or less than 1 year of Canadian work experience"
    )
    one_year: int = Field(
        5,
        description="1 year of Canadian work experience"
    )
    two_years: int = Field(
        7,
        description="2 years of Canadian work experience"
    )
    three_years: int = Field(
        8,
        description="3 years of Canadian work experience"
    )
    four_years: int = Field(
        9,
        description="4 years of Canadian work experience"
    )
    five_years_or_more: int = Field(
        10,
        description="5 years or more of Canadian work experience"
    )


class SpouseWorkExperienceWithoutSpouse(BaseModel):
    """
    Placeholder for cases without spouse or common-law partner.
    This factor is not applicable in these cases.
    """
    not_applicable: Optional[str] = Field(
        None,
        description="This factor does not apply to applicants without a spouse or common-law partner"
    )


class SpouseWorkExperienceFactors(BaseModel):
    """
    Response model containing spouse's Canadian work experience factor calculations.
    """
    with_spouse: SpouseWorkExperienceWithSpouse
    without_spouse: SpouseWorkExperienceWithoutSpouse


def spouse_work_experience_factors() -> SpouseWorkExperienceFactors:
    """
    Factory function that returns the appropriate model.
    """
    return SpouseWorkExperienceFactors(
        with_spouse=SpouseWorkExperienceWithSpouse(),
        without_spouse=SpouseWorkExperienceWithoutSpouse()
    )