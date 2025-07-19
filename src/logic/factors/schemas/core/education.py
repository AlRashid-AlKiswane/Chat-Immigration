from pydantic import BaseModel, Field


class EducationWithSpouseFactors(BaseModel):
    """
    Education points calculation for applicants with a spouse or common-law partner.
    Maximum 140 points.
    """

    less_than_secondary: int = Field(
        0,
        description="Less than secondary school (high school)"
    )
    secondary_diploma: int = Field(
        28,
        description="Secondary diploma (high school graduation)"
    )
    one_year_program: int = Field(
        84,
        description="One-year degree, diploma or certificate from a university, college, trade or technical school, or other institute"
    )
    two_year_program: int = Field(
        91,
        description="Two-year program at a university, college, trade or technical school, or other institute"
    )
    bachelors_or_three_year_program: int = Field(
        112,
        description="Bachelor's degree OR a three or more year program at a university, college, trade or technical school, or other institute"
    )
    two_or_more_credentials: int = Field(
        119,
        description="Two or more certificates, diplomas, or degrees. One must be for a program of three or more years"
    )
    masters_or_professional_degree: int = Field(
        126,
        description="Master's degree OR professional degree needed to practice in a licensed profession (medicine, veterinary medicine, dentistry, optometry, law, chiropractic medicine, pharmacy)"
    )
    doctoral_degree: int = Field(
        140,
        description="Doctoral level university degree (Ph.D.)"
    )


class EducationWithoutSpouseFactors(BaseModel):
    """
    Education points calculation for applicants without a spouse or common-law partner.
    Maximum 150 points.
    """

    less_than_secondary: int = Field(
        0,
        description="Less than secondary school (high school)"
    )
    secondary_diploma: int = Field(
        30,
        description="Secondary diploma (high school graduation)"
    )
    one_year_program: int = Field(
        90,
        description="One-year degree, diploma or certificate from a university, college, trade or technical school, or other institute"
    )
    two_year_program: int = Field(
        98,
        description="Two-year program at a university, college, trade or technical school, or other institute"
    )
    bachelors_or_three_year_program: int = Field(
        120,
        description="Bachelor's degree OR a three or more year program at a university, college, trade or technical school, or other institute"
    )
    two_or_more_credentials: int = Field(
        128,
        description="Two or more certificates, diplomas, or degrees. One must be for a program of three or more years"
    )
    masters_or_professional_degree: int = Field(
        135,
        description="Master's degree OR professional degree needed to practice in a licensed profession (medicine, veterinary medicine, dentistry, optometry, law, chiropractic medicine, pharmacy)"
    )
    doctoral_degree: int = Field(
        150,
        description="Doctoral level university degree (Ph.D.)"
    )


class EducationFactors(BaseModel):
    """
    Response model containing both education factor calculations.
    """
    with_spouse: EducationWithSpouseFactors
    without_spouse: EducationWithoutSpouseFactors


def education_factors() -> EducationFactors:
    return EducationFactors(
        with_spouse=EducationWithSpouseFactors(),
        without_spouse=EducationWithoutSpouseFactors()
    )
