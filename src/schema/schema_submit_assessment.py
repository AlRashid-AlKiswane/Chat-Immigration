

from dataclasses import Field
from datetime import datetime
from typing import Optional
from openai import BaseModel


class AssessmentAnswers(BaseModel):
    marital_status: Optional[str] = None
    age: Optional[int] = None
    spouse_citizen: Optional[str] = None
    spouse_coming: Optional[str] = None
    education_level: Optional[str] = None
    canada_education: Optional[str] = None
    education_eca: Optional[str] = None
    language_test_recent: Optional[str] = None
    first_language_test: Optional[str] = None
    first_language_scores_listening: Optional[str] = None
    first_language_scores_speaking: Optional[str] = None
    first_language_scores_reading: Optional[str] = None
    first_language_scores_writing: Optional[str] = None
    second_language_test: Optional[str] = None
    second_language_scores_listening: Optional[str] = None
    second_language_scores_speaking: Optional[str] = None
    second_language_scores_reading: Optional[str] = None
    second_language_scores_writing: Optional[str] = None
    canadian_work_experience: Optional[str] = None
    foreign_work_experience: Optional[str] = None
    trade_certificate: Optional[str] = None
    job_offer: Optional[str] = None
    noc_teer: Optional[str] = None
    do_have_nomination: Optional[str] = None
    siblings: Optional[str] = None
    spouse_education: Optional[str] = None
    spouse_experience: Optional[str] = None
    spouse_language_test: Optional[str] = None
    spouse_language_scores_listening: Optional[str] = None
    spouse_language_scores_speaking: Optional[str] = None
    spouse_language_scores_reading: Optional[str] = None
    spouse_language_scores_writing: Optional[str] = None

class AssessmentResponse(BaseModel):
    success: bool
    id: str
    message: str
    submission_id: str
    timestamp: datetime
