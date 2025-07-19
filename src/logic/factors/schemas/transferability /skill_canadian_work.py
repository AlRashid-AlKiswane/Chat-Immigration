from pydantic import BaseModel, Field


class CanadianWorkExp1Year(BaseModel):
    """
    Skill Transferability - Canadian Work Experience with 1 year of experience
    Maximum 25 points
    """
    secondary_or_less: int = Field(
        0,
        description="Secondary school (high school) credential or less"
    )
    post_secondary_one_year: int = Field(
        13,
        description="Post-secondary program credential of one year or longer"
    )
    two_or_more_credentials: int = Field(
        25,
        description="Two or more post-secondary credentials with at least one 3+ year program"
    )
    masters_or_professional: int = Field(
        25,
        description="Master's or professional degree (Skill Level A)"
    )
    doctoral: int = Field(
        25,
        description="Doctoral level university degree"
    )


class CanadianWorkExp2PlusYears(BaseModel):
    """
    Skill Transferability - Canadian Work Experience with 2+ years of experience
    Maximum 50 points
    """
    secondary_or_less: int = Field(
        0,
        description="Secondary school (high school) credential or less"
    )
    post_secondary_one_year: int = Field(
        25,
        description="Post-secondary program credential of one year or longer"
    )
    two_or_more_credentials: int = Field(
        50,
        description="Two or more post-secondary credentials with at least one 3+ year program"
    )
    masters_or_professional: int = Field(
        50,
        description="Master's or professional degree (Skill Level A)"
    )
    doctoral: int = Field(
        50,
        description="Doctoral level university degree"
    )


class CanadianWorkExpFactors(BaseModel):
    """
    Combined model for Skill Transferability - Canadian Work Experience factors
    Maximum 100 points total (combined from both work experience scenarios)
    """
    one_year_exp: CanadianWorkExp1Year
    two_plus_years_exp: CanadianWorkExp2PlusYears


def transferability_Canadian_work_exp_factors() -> CanadianWorkExpFactors:
    return CanadianWorkExpFactors(
        one_year_exp=CanadianWorkExp1Year(),
        two_plus_years_exp=CanadianWorkExp2PlusYears()
    )