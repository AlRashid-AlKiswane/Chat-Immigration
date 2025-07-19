from pydantic import BaseModel, Field
from typing import Optional


class SpouseLanguageWithSpouse(BaseModel):
    """
    Spouse's official language proficiency points calculation for applicants with a spouse or common-law partner.
    Maximum 20 points total (5 points max per ability).
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
        5,
        description="CLB 9 or more per ability"
    )


class SpouseLanguageWithoutSpouse(BaseModel):
    """
    Spouse's official language proficiency points calculation for applicants without a spouse or common-law partner.
    This factor does not apply.
    """
    
    not_applicable: Optional[str] = Field(
        None,
        description="This factor does not apply to applicants without a spouse or common-law partner"
    )


class SpouseLanguageFactors(BaseModel):
    """
    Response model containing both spouse's language proficiency factor calculations.
    """
    with_spouse: SpouseLanguageWithSpouse
    without_spouse: SpouseLanguageWithoutSpouse


def spouse_language_factors() -> SpouseLanguageFactors:
    return SpouseLanguageFactors(
        with_spouse=SpouseLanguageWithSpouse(),
        without_spouse=SpouseLanguageWithoutSpouse()
    )