from enum import Enum

class EducationLevel(Enum):
    LESS_THAN_SECONDARY = "less_than_secondary"
    SECONDARY_DIPLOMA = "secondary_diploma"
    ONE_YEAR_POST_SECONDARY = "one_year_post_secondary"
    TWO_YEAR_POST_SECONDARY = "two_year_post_secondary"
    BACHELOR_OR_THREE_YEAR_POST_SECONDARY_OR_MORE = "Bachelor_or_three_year_post_secondary_or_more"
    TWO_OR_MORE_CERTIFICATES = "two_or_more_post_secondary_one_three_year"
    MASTERS_OR_PROFESSIONAL_DEGREE = "masters_or_professional_degree"
    PHD = "phd"


    @classmethod
    def values(cls):
        """helper method that returns all valid values of an Enum as a set."""
        return {member.value for member in cls}
    
    

class LanguageTestEnum(str, Enum):
    """Enum for supported language tests in Express Entry."""
    IELTS = "IELTS"      # English
    CELPIP = "CELPIP"    # English
    TEF = "TEF"          # French
    TCF = "TCF"          # French
    PTE = "PTE"          # English (Pearson Test)

    @classmethod
    def values(cls):
        """
        helper method that returns all valid values of an Enum as a set.
        """
        return {member.value for member in cls}
