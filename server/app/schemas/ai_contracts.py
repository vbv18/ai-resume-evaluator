from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    Structured extraction of candidate resume.
    """
    candidate_name: str | None = None
    skills: list[str] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    total_years_experience: float | None = None

    model_config = ConfigDict(extra="ignore")

    @field_validator("skills", mode="before")
    @classmethod
    def dedupe_skills(cls, v: list[str]) -> list[str]:
        if not v:
            return []
        seen: set[str] = set()
        result = []
        for skill in v:
            normalized = str(skill).strip()
            if normalized and normalized.lower() not in seen:
                seen.add(normalized.lower())
                result.append(normalized)
        return result


class JobDescriptionData(BaseModel):
    """
    Structured extraction of job description requirements.
    """
    job_title: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    min_years_experience: float | None = None
    education_requirements: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


class MatchedSkill(BaseModel):
    skill: str
    proficiency: str = "Intermediate"
    evidence: str = ""


class MissingSkill(BaseModel):
    skill: str
    criticality: str = "REQUIRED"  # REQUIRED or PREFERRED
    recommendation: str = ""


class KeywordAnalysis(BaseModel):
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    density_score: int = Field(ge=0, le=100, default=70)


class ATSFindings(BaseModel):
    formatting_issues: list[str] = Field(default_factory=list)
    readability_assessment: str = "Good"
    actionable_ats_fixes: list[str] = Field(default_factory=list)


class RecommendationItem(BaseModel):
    title: str
    category: str = "Content"
    action: str
    before_example: str | None = None
    after_example: str | None = None


class SectionBreakdowns(BaseModel):
    experience_relevance: str = ""
    education_match: str = ""
    certifications_impact: str = ""


class RawEvaluationResult(BaseModel):
    """
    Structured response returned directly by the AI model.
    Note: Overall score is calculated deterministically by backend.
    """
    ats_score: int = Field(ge=0, le=100)
    job_match_score: int = Field(ge=0, le=100)
    skills_match_score: int = Field(ge=0, le=100)
    experience_match_score: int = Field(ge=0, le=100)
    verdict: str
    executive_summary: str
    matched_skills: list[MatchedSkill] = Field(default_factory=list)
    missing_skills: list[MissingSkill] = Field(default_factory=list)
    keyword_analysis: KeywordAnalysis = Field(default_factory=KeywordAnalysis)
    ats_findings: ATSFindings = Field(default_factory=ATSFindings)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[RecommendationItem] = Field(default_factory=list)
    section_breakdowns: SectionBreakdowns = Field(default_factory=SectionBreakdowns)

    model_config = ConfigDict(extra="ignore")
