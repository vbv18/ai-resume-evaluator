import json
from typing import Any
from groq import APIError, APITimeoutError, AsyncGroq, RateLimitError
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.ai.providers.base import AIProvider
from app.core.config import Settings
from app.core.exceptions import LLMProviderError, LLMResponseValidationError
from app.core.logging import get_logger
from app.lib.constants import MAX_LLM_VALIDATION_RETRIES

logger = get_logger(__name__)


class GroqProvider(AIProvider):
    """
    Groq AI Provider implementation supporting fast inference on models like
    openai/gpt-oss-20b and llama-3.3-70b-versatile.
    """

    def __init__(self, settings: Settings):
        self._client = AsyncGroq(api_key=settings.groq_api_key or "mock_key")
        self._default_model = settings.groq_model
        self._timeout = settings.request_timeout_seconds

    @retry(
        retry=retry_if_exception_type((APITimeoutError, RateLimitError)),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _execute_chat_completion(
        self, *, system_prompt: str, user_content: str, model: str, temperature: float
    ) -> dict[str, Any]:
        response = await self._client.chat.completions.create(
            model=model,
            temperature=temperature,
            timeout=self._timeout,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        )

        content = response.choices[0].message.content or "{}"
        usage = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0,
        }
        return {"content": content, "usage": usage}

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_content: str,
        response_schema: type[BaseModel],
        model: str | None = None,
        temperature: float = 0.1,
    ) -> tuple[BaseModel, dict[str, int]]:
        target_model = model or self._default_model
        last_error: ValidationError | None = None
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        prompt_to_send = system_prompt
        content_to_send = user_content

        for attempt in range(MAX_LLM_VALIDATION_RETRIES + 1):
            try:
                raw_result = await self._execute_chat_completion(
                    system_prompt=prompt_to_send,
                    user_content=content_to_send,
                    model=target_model,
                    temperature=temperature,
                )
            except (APITimeoutError, RateLimitError, APIError) as exc:
                logger.error(
                    "groq_call_failed",
                    error=str(exc),
                    model=target_model,
                    attempt=attempt + 1,
                )
                raise LLMProviderError(
                    f"AI Provider ({target_model}) failed to respond.",
                    details={"provider_error": str(exc)},
                ) from exc

            usage = raw_result["usage"]
            total_usage["prompt_tokens"] += usage.get("prompt_tokens", 0)
            total_usage["completion_tokens"] += usage.get("completion_tokens", 0)
            total_usage["total_tokens"] += usage.get("total_tokens", 0)

            try:
                parsed_json = json.loads(raw_result["content"])
            except json.JSONDecodeError as exc:
                logger.warning("invalid_json_received", attempt=attempt + 1)
                content_to_send = f"{user_content}\n\nYour previous response was not valid JSON. Return strictly valid JSON."
                continue

            try:
                validated_model = response_schema.model_validate(parsed_json)
                return validated_model, total_usage
            except ValidationError as exc:
                last_error = exc
                logger.warning(
                    "schema_validation_failed_retrying",
                    attempt=attempt + 1,
                    errors=exc.errors(),
                )
                # Reflection repair loop
                content_to_send = (
                    f"{user_content}\n\n"
                    f"Your previous response had schema validation errors:\n"
                    f"{exc.errors()}\n\n"
                    f"Fix these errors and output the corrected JSON."
                )

        raise LLMResponseValidationError(
            "AI response did not conform to the expected schema after retry.",
            details={"errors": last_error.errors() if last_error else None},
        )
