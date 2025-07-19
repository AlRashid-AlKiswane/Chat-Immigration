from pydantic import BaseModel, Field


class CertificateCLB5To6(BaseModel):
    """
    Certificate of qualification with CLB 5-6 in all first official language abilities
    Maximum 25 points
    """
    with_certificate: int = Field(
        25,
        description="With a certificate of qualification in a trade occupation"
    )


class CertificateCLB7Plus(BaseModel):
    """
    Certificate of qualification with CLB 7+ in all first official language abilities
    Maximum 50 points
    """
    with_certificate: int = Field(
        50,
        description="With a certificate of qualification in a trade occupation"
    )


class CertificateFactors(BaseModel):
    """
    Combined model for Certificate of Qualification with Language Proficiency
    Maximum 50 points total
    """
    clb5_to_6: CertificateCLB5To6 = Field(
        ...,
        description="Points with CLB 5-6 in all first official language abilities"
    )
    clb7_plus: CertificateCLB7Plus = Field(
        ...,
        description="Points with CLB 7+ in all first official language abilities"
    )


def certificate_factors() -> CertificateFactors:
    return CertificateFactors(
        clb5_to_6=CertificateCLB5To6(),
        clb7_plus=CertificateCLB7Plus()
    )