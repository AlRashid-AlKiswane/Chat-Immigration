from pydantic import BaseModel, Field


class SecondLanguageWithSpouse(BaseModel):
    """
    Second official language proficiency points calculation for applicants with a spouse or common-law partner.
    Maximum 22 points combined across all abilities (6 points max per ability).
    """
    
    clb_4_or_less: int = Field(
        0,
        description="CLB 4 or less per ability"
    )
    clb_5_or_6: int = Field(
        1,
        description="CLB 5 or 6 per ability"
    )
    clb_7_or_8: int = Field(
        3,
        description="CLB 7 or 8 per ability"
    )
    clb_9_or_more: int = Field(
        6,
        description="CLB 9 or more per ability"
    )


class SecondLanguageWithoutSpouse(BaseModel):
    """
    Second official language proficiency points calculation for applicants without a spouse or common-law partner.
    Maximum 24 points combined across all abilities (6 points max per ability).
    """
    
    clb_4_or_less: int = Field(
        0,
        description="CLB 4 or less per ability"
    )
    clb_5_or_6: int = Field(
        1,
        description="CLB 5 or 6 per ability"
    )
    clb_7_or_8: int = Field(
        3,
        description="CLB 7 or 8 per ability"
    )
    clb_9_or_more: int = Field(
        6,
        description="CLB 9 or more per ability"
    )


class SecondLanguageFactors(BaseModel):
    """
    Response model containing both second language proficiency factor calculations.
    """
    with_spouse: SecondLanguageWithSpouse
    without_spouse: SecondLanguageWithoutSpouse


def second_language_factors() -> SecondLanguageFactors:
    return SecondLanguageFactors(
        with_spouse=SecondLanguageWithSpouse(),
        without_spouse=SecondLanguageWithoutSpouse()
    )