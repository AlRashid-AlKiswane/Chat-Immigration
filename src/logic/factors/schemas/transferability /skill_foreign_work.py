from pydantic import BaseModel, Field


class ForeignWorkExpCLB7To8(BaseModel):
    """
    Foreign work experience with CLB 7-8 in all first official language abilities
    Maximum 25 points
    """
    no_experience: int = Field(
        0,
        description="No foreign work experience"
    )
    one_or_two_years: int = Field(
        13,
        description="1 or 2 years of foreign work experience"
    )
    three_plus_years: int = Field(
        25,
        description="3 years or more of foreign work experience"
    )


class ForeignWorkExpCLB9Plus(BaseModel):
    """
    Foreign work experience with CLB 9+ in all first official language abilities
    Maximum 50 points
    """
    no_experience: int = Field(
        0,
        description="No foreign work experience"
    )
    one_or_two_years: int = Field(
        25,
        description="1 or 2 years of foreign work experience"
    )
    three_plus_years: int = Field(
        25,
        description="3 years or more of foreign work experience"
    )


class ForeignWorkExpFactors(BaseModel):
    """
    Combined model for Foreign Work Experience with Language Proficiency
    Maximum 75 points total (combined from both language scenarios)
    """
    clb7_to_8: ForeignWorkExpCLB7To8 = Field(
        ...,
        description="Points with CLB 7-8 in all first official language abilities"
    )
    clb9_plus: ForeignWorkExpCLB9Plus = Field(
        ...,
        description="Points with CLB 9+ in all first official language abilities"
    )


def foreign_work_exp_factors() -> ForeignWorkExpFactors:
    return ForeignWorkExpFactors(
        clb7_to_8=ForeignWorkExpCLB7To8(),
        clb9_plus=ForeignWorkExpCLB9Plus()
    )