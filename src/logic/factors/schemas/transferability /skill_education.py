from pydantic import BaseModel, Field


class TransferabilityEducationCLB7To8(BaseModel):
    """
    Skill Transferability - Education with CLB 7-8 in all first official language abilities
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


class TransferabilityEducationCLB9Plus(BaseModel):
    """
    Skill Transferability - Education with CLB 9+ in all first official language abilities
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


class TransferabilityEducationFactors(BaseModel):
    """
    Combined model for Skill Transferability - Education factors
    Maximum 100 points total (combined from both language scenarios)
    """
    clb7_to_8: TransferabilityEducationCLB7To8
    clb9_plus: TransferabilityEducationCLB9Plus


def transferability_education_factors() -> TransferabilityEducationFactors:
    return TransferabilityEducationFactors(
        clb7_to_8=TransferabilityEducationCLB7To8(),
        clb9_plus=TransferabilityEducationCLB9Plus()
    )
