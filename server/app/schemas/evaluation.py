import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.ai_contracts import (
    ATSFindings,
    KeywordAnalysis,
    MatchedSkill,
    MissingSkill,
    RecommendationItem,
    SectionBreakdowns,
)


class EvaluationCreate(BaseModel):
    resume_version_id: uuid.UUID
    job_description_version_id: uuid.UUID
    ai_provider: str | None = None
    model_name: str | None = None


class EvaluationEnqueueResponse(BaseModel):
    evaluation_id: uuid.UUID
    status: str = "QUEUED"
    message: str = "Evaluation has been queued for background processing."


class EvaluationStatusResponse(BaseModel):
    evaluation_id: uuid.UUID
    status: str  # QUEUED, PROCESSING, COMPLETED, FAILED, CANCELLED
    progress_percentage: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None


class EvaluationResultResponse(BaseModel):
    id: uuid.UUID
    evaluation_run_id: uuid.UUID
    executive_summary: str
    matched_skills: list[MatchedSkill]
    missing_skills: list[MissingSkill]
    keyword_analysis: KeywordAnalysis
    ats_findings: ATSFindings
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[RecommendationItem]
    section_breakdowns: SectionBreakdowns
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvaluationFullResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    resume_version_id: uuid.UUID
    job_description_version_id: uuid.UUID
    status: str
    ai_provider: str
    model_name: str
    prompt_version: str
    rubric_version: str

    overall_score: int | None = None
    ats_score: int | None = None
    job_match_score: int | None = None
    skills_match_score: int | None = None
    experience_match_score: int | None = None
    verdict: str | None = None

    duration_ms: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None

    result: EvaluationResultResponse | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class EvalRunListItem(BaseModel):
    id: uuid.UUID
    resume_version_id: uuid.UUID
    job_description_version_id: uuid.UUID
    status: str
    overall_score: int | None
    verdict: str | None
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ScoreDiffItem(BaseModel):
    category: str
    score_a: int
    score_b: int
    delta: int


class EvaluationComparisonResponse(BaseModel):
    run_a: EvaluationFullResponse
    run_b: EvaluationFullResponse
    overall_delta: int
    score_diffs: list[ScoreDiffItem]
    newly_matched_skills: list[str]
    still_missing_skills: list[str]
