from enum import Enum
from signal import default_int_handler
from pydantic import BaseModel, Field, field_validator


# Resume Extraction


class Experience(BaseModel):
    title: str
    company: str | None = None
    duration: str | None = None
    description: str | None = None


class Education(BaseModel):
    degree: str
    institution: str | None = None
    year: str | None = None


class ResumeData(BaseModel):
    """
    Structured output of LLM Call
    """

    candidate_name: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    total_years_experience: float | None = None

    @field_validator("skills", mode="before")
    @classmethod
    def dedupe_skills(cls, v: list[str]) -> list[str]:
        if not v:
            return []
        seen: set[str] = set[str]()
        result = []
        for skill in v:
            normalized = skill.strip()
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                result.append(normalized)
        return result


# Job Description Extraction


class JobDescriptionData(BaseModel):
    """
    Structured output of LLM Call #2.
    """

    job_title: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_years_experience: float | None = None
    education_requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)


# Evaluation


class Verdict(str, Enum):
    excellent_match = "Excellent Match"
    good_match = "Good Match"
    moderate_match = "Moderate Match"
    weak_match = "Weak Match"
    not_a_match = "Not a Match"


class EvaluationResult(BaseModel):
    """
    Structured output of LLM Call #3 — the final API response payload.
    """

    score: int = Field(ge=0, le=100)
    verdict: Verdict
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    reasoning: str


class EvaluationResponse(BaseModel):
    """Full API response, including intermediate extracted data for transparency/debugging."""

    resume_data: ResumeData
    job_description_data: JobDescriptionData
    evaluation: EvaluationResult


class HealthResponse(BaseModel):
    status: str
    environment: str
