from enum import Enum

class EducationLevel(Enum):
    LESS_THAN_SECONDARY = "less_than_secondary"
    SECONDARY_DIPLOMA = "secondary_diploma"
    ONE_YEAR_POST_SECONDARY = "one_year_post_secondary"
    TWO_YEAR_POST_SECONDARY = "two_year_post_secondary"
    THREE_YEAR_POST_SECONDARY_OR_MORE = "three_year_post_secondary_or_more"
    TWO_OR_MORE_POST_SECONDARY = "two_or_more_post_secondary_one_three_year"
    MASTERS_OR_PROFESSIONAL_DEGREE = "masters_or_professional_degree"
    PHD = "phd"


    @classmethod
    def values(cls):
        """helper method that returns all valid values of an Enum as a set."""
        return {member.value for member in cls}


class LanguageAbility(Enum):
    READING = "reading"
    WRITING = "writing"
    LISTENING = "listening"
    SPEAKING = "speaking"

    @classmethod
    def values(cls):
        """
        helper method that returns all valid values of an Enum as a set.
        """
        return {member.value for member in cls}
