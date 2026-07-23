import asyncio
from fileinput import filename

from fastapi import APIRouter, Depends, Form, Request, UploadFile, status

from app.core.config import Settings, get_settings
from app.core.exceptions import EmptyResumeTextError, FileTooLargeError
from app.core.logging import get_logger
from app.models.schemas import EvaluationResponse
from app.services.evaluation_service import evaluate_match
from app.services.extraction_service import (
    extract_job_description_data,
    extract_resume_data,
)
from app.services.llm_client import LLMClient
from app.services.resume_parser import extract_resume_text
from app.services.token_estimator import ensure_within_limit

router = APIRouter()

logger = get_logger(__name__)


def get_llm_client(request: Request) -> LLMClient:
    """
    Reuse the single LLMClient created at app startup
    """
    return request.app.state.llm_client


@router.post(
    "/evaluate",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    tags=["evaluation"],
)
async def evaluate_resume(
    resume: UploadFile,
    job_description: str = Form(..., min_length=20),
    settings: Settings = Depends(get_settings),
    llm: LLMClient = Depends(get_llm_client),
) -> EvaluationResponse:
    file_bytes = await resume.read()

    if len(file_bytes) > settings.max_upload_size_bytes:
        raise FileTooLargeError(
            f"Resume exceeds the {settings.max_upload_size_mb}MB uplad limit.",
            details={"size_bytes": len(file_bytes)},
        )

    resume_text = extract_resume_text(
        resume.filename or "resume", resume.content_type, file_bytes
    )

    jd_text = job_description.strip()
    if len(jd_text) < 20:
        raise EmptyResumeTextError("Job description text is too short to evaluate.")

    ensure_within_limit(
        resume_text, max_tokens=settings.max_input_tokens, context="Resume"
    )

    ensure_within_limit(
        jd_text, max_tokens=settings.max_input_tokens, context="Job description"
    )

    logger.info(
        "evaluation_started",
        filename=resume.filename,
        resume_chars=len(resume_text),
        jd_chars=len(jd_text),
    )

    # Calls #1 and #2 are independent — run them concurrently rather than sequentially.
    resume_data, jd_data = await asyncio.gather(
        extract_resume_data(llm, resume_text),
        extract_job_description_data(llm, jd_text),
    )

    # Call #3
    evaluation = await evaluate_match(
        llm, resume_data=resume_data, job_description_data=jd_data
    )

    logger.info(
        "evaluation_completed", score=evaluation.score, verdict=evaluation.verdict.value
    )

    return EvaluationResponse(
        resume_data=resume_data, job_description_data=jd_data, evaluation=evaluation
    )
