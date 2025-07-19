from pydantic import BaseModel, Field


class FirstLanguageWithSpouse(BaseModel):
    """
    Language proficiency points calculation for applicants with a spouse or common-law partner.
    Maximum 128 points (32 points per ability x 4 abilities).
    """
    
    less_than_clb_4: int = Field(
        0,
        description="Less than CLB 4 in any ability"
    )
    clb_4_or_5: int = Field(
        6,
        description="CLB 4 or 5 per ability"
    )
    clb_6: int = Field(
        8,
        description="CLB 6 per ability"
    )
    clb_7: int = Field(
        16,
        description="CLB 7 per ability"
    )
    clb_8: int = Field(
        22,
        description="CLB 8 per ability"
    )
    clb_9: int = Field(
        29,
        description="CLB 9 per ability"
    )
    clb_10_or_more: int = Field(
        32,
        description="CLB 10 or more per ability"
    )


class FirstLanguageWithoutSpouse(BaseModel):
    """
    Language proficiency points calculation for applicants without a spouse or common-law partner.
    Maximum 136 points (34 points per ability x 4 abilities).
    """
    
    less_than_clb_4: int = Field(
        0,
        description="Less than CLB 4 in any ability"
    )
    clb_4_or_5: int = Field(
        6,
        description="CLB 4 or 5 per ability"
    )
    clb_6: int = Field(
        9,
        description="CLB 6 per ability"
    )
    clb_7: int = Field(
        17,
        description="CLB 7 per ability"
    )
    clb_8: int = Field(
        23,
        description="CLB 8 per ability"
    )
    clb_9: int = Field(
        31,
        description="CLB 9 per ability"
    )
    clb_10_or_more: int = Field(
        34,
        description="CLB 10 or more per ability"
    )


class FirstLanguageFactors(BaseModel):
    """
    Response model containing both language proficiency factor calculations.
    """
    with_spouse: FirstLanguageWithSpouse
    without_spouse: FirstLanguageWithoutSpouse


def first_language_factors() -> FirstLanguageFactors:
    return LanguageProficiencyFactors(
        with_spouse=FirstLanguageWithSpouse(),
        without_spouse=FirstLanguageWithoutSpouse()
    )