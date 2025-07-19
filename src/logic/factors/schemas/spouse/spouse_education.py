from pydantic import BaseModel, Field
from typing import Optional


class SpouseEducationWithSpouse(BaseModel):
    """
    Spouse's education points calculation for applicants with a spouse or common-law partner.
    Maximum 10 points.
    """
    
    less_than_secondary: int = Field(
        0,
        description="Less than secondary school (high school)"
    )
    secondary_diploma: int = Field(
        2,
        description="Secondary school (high school graduation)"
    )
    one_year_program: int = Field(
        6,
        description="One-year program at a university, college, trade or technical school"
    )
    two_year_program: int = Field(
        7,
        description="Two-year program at a university, college, trade or technical school"
    )
    bachelors_or_three_year: int = Field(
        8,
        description="Bachelor's degree OR a three or more year program"
    )
    two_or_more_credentials: int = Field(
        9,
        description="Two or more certificates, diplomas, or degrees (one 3+ years)"
    )
    masters_or_professional: int = Field(
        10,
        description="Master's or professional degree (medicine, law, etc.)"
    )
    doctoral_degree: int = Field(
        10,
        description="Doctoral level university degree (PhD)"
    )


class SpouseEducationWithoutSpouse(BaseModel):
    """
    Spouse's education points calculation for applicants without a spouse or common-law partner.
    Always returns None as this doesn't apply.
    """
    
    not_applicable: Optional[str] = Field(
        None,
        description="This factor does not apply to applicants without a spouse or common-law partner"
    )


class SpouseEducationFactors(BaseModel):
    """
    Response model containing spouse's education factor calculations.
    """
    with_spouse: SpouseEducationWithSpouse
    without_spouse: SpouseEducationWithoutSpouse


def spouse_education_factors() -> SpouseEducationFactors:
    return SpouseEducationFactors(
        with_spouse=SpouseEducationWithSpouse(),
        without_spouse=SpouseEducationWithoutSpouse()
    )