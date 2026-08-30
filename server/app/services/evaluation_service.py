import json
import time
import uuid
from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.base import AIProvider
from app.ai.scoring import calculate_overall_score, determine_verdict
from app.core.config import Settings
from app.core.exceptions import ResourceNotFoundError
from app.core.logging import get_logger
from app.lib.constants import (
    CURRENT_PROMPT_VERSION,
    CURRENT_RUBRIC_VERSION,
    EVALUATION_SYSTEM_PROMPT,
)
from app.models.evaluation_result import EvaluationResult
from app.models.evaluation_run import EvaluationRun
from app.repositories.evaluation_repo import EvaluationRepository
from app.repositories.job_description_repo import JobDescriptionRepository
from app.repositories.resume_version_repo import ResumeVersionRepository
from app.schemas.ai_contracts import RawEvaluationResult
from app.schemas.evaluation import (
    EvaluationComparisonResponse,
    EvaluationCreate,
    EvaluationFullResponse,
    EvaluationResultResponse,
    EvaluationStatusResponse,
    ScoreDiffItem,
)

logger = get_logger(__name__)


class EvaluationService:
    def __init__(
        self,
        session: AsyncSession,
        ai_provider: AIProvider,
        settings: Settings,
    ):
        self.session = session
        self.ai = ai_provider
        self.settings = settings
        self.eval_repo = EvaluationRepository(session)
        self.resume_version_repo = ResumeVersionRepository(session)
        self.jd_repo = JobDescriptionRepository(session)

    async def enqueue_evaluation(
        self, user_id: uuid.UUID, payload: EvaluationCreate
    ) -> EvaluationRun:
        # Verify ownership of resume version
        resume_version = await self.resume_version_repo.get_by_id_and_user(
            payload.resume_version_id, user_id
        )
        if not resume_version:
            raise ResourceNotFoundError("Resume version was not found.")

        # Verify ownership of job description version
        jd_version = await self.jd_repo.get_version_by_id_and_user(
            payload.job_description_version_id, user_id
        )
        if not jd_version:
            raise ResourceNotFoundError("Job description version was not found.")

        ai_provider_name = payload.ai_provider or self.settings.ai_provider
        model_name = payload.model_name or self.settings.groq_model

        run = EvaluationRun(
            user_id=user_id,
            resume_version_id=payload.resume_version_id,
            job_description_version_id=payload.job_description_version_id,
            status="QUEUED",
            ai_provider=ai_provider_name,
            model_name=model_name,
            prompt_version=CURRENT_PROMPT_VERSION,
            rubric_version=CURRENT_RUBRIC_VERSION,
        )
        await self.eval_repo.create(run)
        return run

    async def process_evaluation_run(self, run_id: uuid.UUID) -> None:
        """
        Executes the AI evaluation for a claimed run.
        Calculates overall score deterministically from AI sub-scores.
        """
        run = await self.eval_repo.get_with_result_by_id(run_id)
        if not run or run.status != "PROCESSING":
            return

        start_time = time.perf_counter()

        try:
            resume_version = await self.resume_version_repo.get_by_id(run.resume_version_id)
            jd_version = await self.jd_repo.get_version_by_id(run.job_description_version_id)

            if not resume_version or not jd_version:
                raise ResourceNotFoundError("Resume version or Job description version missing.")

            comparison_payload = (
                f"<candidate_resume_data>\n{json.dumps(resume_version.structured_data, indent=2)}\n</candidate_resume_data>\n\n"
                f"<target_job_description_data>\n{json.dumps(jd_version.structured_data, indent=2)}\n</target_job_description_data>"
            )

            raw_eval, usage = await self.ai.generate_structured(
                system_prompt=EVALUATION_SYSTEM_PROMPT,
                user_content=comparison_payload,
                response_schema=RawEvaluationResult,
                model=run.model_name,
            )
            raw_eval_data: RawEvaluationResult = raw_eval  # type: ignore

            # Deterministic backend calculation of final overall score
            overall_score = calculate_overall_score(
                ats_score=raw_eval_data.ats_score,
                job_match_score=raw_eval_data.job_match_score,
                skills_match_score=raw_eval_data.skills_match_score,
                experience_match_score=raw_eval_data.experience_match_score,
            )
            verdict = determine_verdict(overall_score)

            duration_ms = int((time.perf_counter() - start_time) * 1000)

            # Persist evaluation result (hybrid relational + JSONB)
            result = EvaluationResult(
                evaluation_run_id=run.id,
                executive_summary=raw_eval_data.executive_summary,
                matched_skills=[s.model_dump() for s in raw_eval_data.matched_skills],
                missing_skills=[s.model_dump() for s in raw_eval_data.missing_skills],
                keyword_analysis=raw_eval_data.keyword_analysis.model_dump(),
                ats_findings=raw_eval_data.ats_findings.model_dump(),
                strengths=raw_eval_data.strengths,
                weaknesses=raw_eval_data.weaknesses,
                recommendations=[r.model_dump() for r in raw_eval_data.recommendations],
                section_breakdowns=raw_eval_data.section_breakdowns.model_dump(),
                sanitized_ai_response={
                    "model": run.model_name,
                    "prompt_version": run.prompt_version,
                    "rubric_version": run.rubric_version,
                },
            )
            await self.eval_repo.create_result(result)

            # Update run to COMPLETED
            run.status = "COMPLETED"
            run.overall_score = overall_score
            run.ats_score = raw_eval_data.ats_score
            run.job_match_score = raw_eval_data.job_match_score
            run.skills_match_score = raw_eval_data.skills_match_score
            run.experience_match_score = raw_eval_data.experience_match_score
            run.verdict = verdict
            run.duration_ms = duration_ms
            run.prompt_tokens = usage.get("prompt_tokens", 0)
            run.completion_tokens = usage.get("completion_tokens", 0)
            run.total_tokens = usage.get("total_tokens", 0)
            run.completed_at = datetime.now(timezone.utc)
            await self.session.commit()

            logger.info(
                "evaluation_completed_successfully",
                run_id=str(run.id),
                overall_score=overall_score,
                duration_ms=duration_ms,
            )

        except Exception as exc:
            logger.error("evaluation_processing_failed", run_id=str(run.id), error=str(exc))
            run.status = "FAILED"
            run.error_code = type(exc).__name__
            run.error_message = str(exc)
            run.completed_at = datetime.now(timezone.utc)
            await self.session.commit()

    async def get_status(
        self, run_id: uuid.UUID, user_id: uuid.UUID
    ) -> EvaluationStatusResponse:
        run = await self.eval_repo.get_by_id_and_user(run_id, user_id)
        if not run:
            raise ResourceNotFoundError(f"Evaluation run {run_id} was not found.")

        progress_map = {
            "QUEUED": 20,
            "PROCESSING": 65,
            "COMPLETED": 100,
            "FAILED": 100,
            "CANCELLED": 100,
        }
        return EvaluationStatusResponse(
            evaluation_id=run.id,
            status=run.status,
            progress_percentage=progress_map.get(run.status, 0),
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_code=run.error_code,
            error_message=run.error_message,
        )

    async def get_full_evaluation(
        self, run_id: uuid.UUID, user_id: uuid.UUID
    ) -> EvaluationFullResponse:
        run = await self.eval_repo.get_with_result(run_id, user_id)
        if not run:
            raise ResourceNotFoundError(f"Evaluation run {run_id} was not found.")

        result_response = None
        if run.result:
            result_response = EvaluationResultResponse(
                id=run.result.id,
                evaluation_run_id=run.result.evaluation_run_id,
                executive_summary=run.result.executive_summary,
                matched_skills=run.result.matched_skills,  # type: ignore
                missing_skills=run.result.missing_skills,  # type: ignore
                keyword_analysis=run.result.keyword_analysis,  # type: ignore
                ats_findings=run.result.ats_findings,  # type: ignore
                strengths=run.result.strengths,
                weaknesses=run.result.weaknesses,
                recommendations=run.result.recommendations,  # type: ignore
                section_breakdowns=run.result.section_breakdowns,  # type: ignore
                created_at=run.result.created_at,
            )

        return EvaluationFullResponse(
            id=run.id,
            user_id=run.user_id,
            resume_version_id=run.resume_version_id,
            job_description_version_id=run.job_description_version_id,
            status=run.status,
            ai_provider=run.ai_provider,
            model_name=run.model_name,
            prompt_version=run.prompt_version,
            rubric_version=run.rubric_version,
            overall_score=run.overall_score,
            ats_score=run.ats_score,
            job_match_score=run.job_match_score,
            skills_match_score=run.skills_match_score,
            experience_match_score=run.experience_match_score,
            verdict=run.verdict,
            duration_ms=run.duration_ms,
            prompt_tokens=run.prompt_tokens,
            completion_tokens=run.completion_tokens,
            total_tokens=run.total_tokens,
            result=result_response,
            created_at=run.created_at,
            started_at=run.started_at,
            completed_at=run.completed_at,
        )

    async def list_user_evaluations(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 20
    ) -> Sequence[EvaluationRun]:
        return await self.eval_repo.list_runs_by_user(user_id, skip=skip, limit=limit)

    async def compare_evaluations(
        self, run_a_id: uuid.UUID, run_b_id: uuid.UUID, user_id: uuid.UUID
    ) -> EvaluationComparisonResponse:
        run_a = await self.get_full_evaluation(run_a_id, user_id)
        run_b = await self.get_full_evaluation(run_b_id, user_id)

        score_a = run_a.overall_score or 0
        score_b = run_b.overall_score or 0
        overall_delta = score_b - score_a

        score_diffs = [
            ScoreDiffItem(
                category="Overall Fit",
                score_a=score_a,
                score_b=score_b,
                delta=overall_delta,
            ),
            ScoreDiffItem(
                category="ATS Compatibility",
                score_a=run_a.ats_score or 0,
                score_b=run_b.ats_score or 0,
                delta=(run_b.ats_score or 0) - (run_a.ats_score or 0),
            ),
            ScoreDiffItem(
                category="Job Description Match",
                score_a=run_a.job_match_score or 0,
                score_b=run_b.job_match_score or 0,
                delta=(run_b.job_match_score or 0) - (run_a.job_match_score or 0),
            ),
            ScoreDiffItem(
                category="Hard Skills",
                score_a=run_a.skills_match_score or 0,
                score_b=run_b.skills_match_score or 0,
                delta=(run_b.skills_match_score or 0) - (run_a.skills_match_score or 0),
            ),
            ScoreDiffItem(
                category="Experience Relevance",
                score_a=run_a.experience_match_score or 0,
                score_b=run_b.experience_match_score or 0,
                delta=(run_b.experience_match_score or 0) - (run_a.experience_match_score or 0),
            ),
        ]

        # Skill difference calculation
        skills_a = {s.skill.lower() for s in run_a.result.matched_skills} if run_a.result else set()
        skills_b = {s.skill.lower() for s in run_b.result.matched_skills} if run_b.result else set()

        newly_matched = [s.skill for s in run_b.result.matched_skills if s.skill.lower() not in skills_a] if run_b.result else []
        still_missing = [s.skill for s in run_b.result.missing_skills] if run_b.result else []

        return EvaluationComparisonResponse(
            run_a=run_a,
            run_b=run_b,
            overall_delta=overall_delta,
            score_diffs=score_diffs,
            newly_matched_skills=newly_matched,
            still_missing_skills=still_missing,
        )
