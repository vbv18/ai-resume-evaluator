from pydantic import ValidationError, BaseModel
from app.core.exceptions import LLMResponseValidationError
from app.core.logging import get_logger
from app.models.schemas import JobDescriptionData, ResumeData
from app.lib.prompts import JOB_DESCRIPTION_EXTRACTION_PROMPT, RESUME_EXTRACTION_PROMPT
from app.services.llm_client import LLMClient
from typing import TypeVar

T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)

_MAX_VALIDATION_RETRIES = 1


async def _extract_and_validate(
    llm: LLMClient,
    *,
    system_prompt,
    content: str,
    model_cls: type[T],
    label: str,
) -> T:
    last_error: ValidationError | None = None

    for attempt in range(_MAX_VALIDATION_RETRIES + 1):
        payload = await llm.get_json_completion(
            system_prompt=system_prompt, user_content=content
        )
        try:
            return (
                model_cls.model_validate(payload["data"]),
                payload["usage"],
            )
        except ValidationError as exc:
            last_error = exc
            logger.warning(
                "llm_output_validation_failed",
                label=label,
                attempt=attempt + 1,
                errors=exc.errors(),
            )

    raise LLMResponseValidationError(
        f"The AI's {label} output did not match the expected structure after retrying.",
        details={"errors": last_error.errors() if last_error else None},
    )


async def extract_resume_data(llm: LLMClient, resume_text: str) -> ResumeData:
    return await _extract_and_validate(
        llm,
        system_prompt=RESUME_EXTRACTION_PROMPT,
        content=resume_text,
        model_cls=ResumeData,
        label="resume extraction",
    )


async def extract_job_description_data(
    llm: LLMClient, jd_text: str
) -> JobDescriptionData:
    return await _extract_and_validate(
        llm,
        system_prompt=JOB_DESCRIPTION_EXTRACTION_PROMPT,
        content=jd_text,
        model_cls=JobDescriptionData,
        label="job description extraction",
    )
