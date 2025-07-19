from pydantic import BaseModel, Field


class ForeignWith1YearCanadian(BaseModel):
    """
    Foreign work experience with 1 year of Canadian work experience
    Maximum 25 points
    """
    no_foreign_exp: int = Field(
        0,
        description="No foreign work experience"
    )
    one_or_two_years_foreign: int = Field(
        13,
        description="1 or 2 years of foreign work experience"
    )
    three_plus_years_foreign: int = Field(
        25,
        description="3 years or more of foreign work experience"
    )


class ForeignWith2PlusYearsCanadian(BaseModel):
    """
    Foreign work experience with 2+ years of Canadian work experience
    Maximum 50 points
    """
    no_foreign_exp: int = Field(
        0,
        description="No foreign work experience"
    )
    one_or_two_years_foreign: int = Field(
        25,
        description="1 or 2 years of foreign work experience"
    )
    three_plus_years_foreign: int = Field(
        50,
        description="3 years or more of foreign work experience"
    )


class ForeignWithCanadianWorkExpFactors(BaseModel):
    """
    Combined model for Foreign Work Experience with Canadian Work Experience
    Maximum 100 points total (combined from both Canadian experience scenarios)
    """
    with_1_year_canadian: ForeignWith1YearCanadian = Field(
        ...,
        description="Points with 1 year of Canadian work experience"
    )
    with_2_plus_years_canadian: ForeignWith2PlusYearsCanadian = Field(
        ...,
        description="Points with 2+ years of Canadian work experience"
    )


def foreign_with_canadian_exp_factors() -> ForeignWithCanadianWorkExpFactors:
    return ForeignWithCanadianWorkExpFactors(
        with_1_year_canadian=ForeignWith1YearCanadian(),
        with_2_plus_years_canadian=ForeignWith2PlusYearsCanadian()
    )