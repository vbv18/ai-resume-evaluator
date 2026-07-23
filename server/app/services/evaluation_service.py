from pydantic import ValidationError
from app.core.exceptions import LLMResponseValidationError
from app.core.logging import get_logger
from app.models.schemas import EvaluationResult, JobDescriptionData, ResumeData
from app.prompts.prompts import EVALUATION_PROMPT
from app.services.llm_client import LLMClient

logger = get_logger(__name__)

_MAX_VALIDATION_RETRIES = 1


async def evaluate_match(
    llm: LLMClient,
    *,
    resume_data: ResumeData,
    job_description_data: JobDescriptionData,
) -> EvaluationResult:
    comparison_payload = (
        f"RESUME_DATA:\n{resume_data.model_dump_json()}\n\n"
        f"JOB_DESCRIPTION_DATA:\n{job_description_data.model_dump_json()}"
    )

    last_error: ValidationError | None = None

    for attempt in range(_MAX_VALIDATION_RETRIES + 1):
        payload = await llm.get_json_completion(
            system_prompt=EVALUATION_PROMPT, user_content=comparison_payload
        )
        try:
            return (
                EvaluationResult.model_validate(payload["data"]),
                payload["usage"],
            )
        except ValidationError as exc:
            last_error = exc
            logger.warning(
                "evaluation_validation_failed", attempt=attempt + 1, errors=exc.errors()
            )

    raise LLMResponseValidationError(
        "The AI's evaluation output did not match the expected structure after retrying.",
        details={"errors": last_error.errors() if last_error else None},
    )
