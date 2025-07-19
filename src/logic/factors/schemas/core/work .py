from pydantic import BaseModel, Field


class CanadianWorkExperienceWithSpouse(BaseModel):
    """
    Canadian work experience points calculation for applicants with a spouse or common-law partner.
    Maximum 70 points.
    """
    
    none_or_less_than_year: int = Field(
        0,
        description="None or less than 1 year of Canadian work experience"
    )
    one_year: int = Field(
        35,
        description="1 year of Canadian work experience"
    )
    two_years: int = Field(
        46,
        description="2 years of Canadian work experience"
    )
    three_years: int = Field(
        56,
        description="3 years of Canadian work experience"
    )
    four_years: int = Field(
        63,
        description="4 years of Canadian work experience"
    )
    five_years_or_more: int = Field(
        70,
        description="5 years or more of Canadian work experience"
    )


class CanadianWorkExperienceWithoutSpouse(BaseModel):
    """
    Canadian work experience points calculation for applicants without a spouse or common-law partner.
    Maximum 80 points.
    """
    
    none_or_less_than_year: int = Field(
        0,
        description="None or less than 1 year of Canadian work experience"
    )
    one_year: int = Field(
        40,
        description="1 year of Canadian work experience"
    )
    two_years: int = Field(
        53,
        description="2 years of Canadian work experience"
    )
    three_years: int = Field(
        64,
        description="3 years of Canadian work experience"
    )
    four_years: int = Field(
        72,
        description="4 years of Canadian work experience"
    )
    five_years_or_more: int = Field(
        80,
        description="5 years or more of Canadian work experience"
    )


class CanadianWorkExperienceFactors(BaseModel):
    """
    Response model containing both Canadian work experience factor calculations.
    """
    with_spouse: CanadianWorkExperienceWithSpouse
    without_spouse: CanadianWorkExperienceWithoutSpouse


def canadian_work_experience_factors() -> CanadianWorkExperienceFactors:
    return CanadianWorkExperienceFactors(
        with_spouse=CanadianWorkExperienceWithSpouse(),
        without_spouse=CanadianWorkExperienceWithoutSpouse()
    )