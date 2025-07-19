from pydantic import BaseModel, Field


class AdditionalPoints(BaseModel):
    """
    Additional points in the Comprehensive Ranking System (CRS)
    Maximum 600 points total
    """
    
    sibling_in_canada: int = Field(
        15,
        description="Brother or sister living in Canada who is a citizen or permanent resident"
    )
    
    french_nclc7_no_english: int = Field(
        25,
        description="NCLC 7+ on all four French skills and CLB 4 or lower in English (or no English test)"
    )
    
    french_nclc7_english_clb5: int = Field(
        50,
        description="NCLC 7+ on all four French skills and CLB 5+ on all four English skills"
    )
    
    post_secondary_1_2_years: int = Field(
        15,
        description="Post-secondary education in Canada - credential of one or two years"
    )
    
    post_secondary_3_plus_years: int = Field(
        30,
        description="Post-secondary education in Canada - credential three years or longer"
    )
    
    provincial_nomination: int = Field(
        600,
        description="Provincial or territorial nomination"
    )


def additional_points_factors() -> AdditionalPoints:
    return AdditionalPoints()