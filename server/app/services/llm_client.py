import json
from groq import APIError, APITimeoutError, AsyncGroq, RateLimitError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import Settings
from app.core.exceptions import LLMProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self, settings: Settings):
        self._client = AsyncGroq(api_key=settings.groq_api_key)
        self._model = settings.groq_model
        self._timeout = settings.request_timeout_seconds

    @retry(
        retry=retry_if_exception_type((APITimeoutError, RateLimitError)),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _create_completion(self, *, system_prompt: str, user_content: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            temperature=0.1,
            timeout=self._timeout,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
        )

        return response.choices[0].message.content or ""

    async def get_json_completion(
        self, *, system_prompt: str, user_content: str
    ) -> dict:
        try:
            raw = await self._create_completion(
                system_prompt=system_prompt, user_content=user_content
            )
        except (APITimeoutError, RateLimitError, APIError) as exc:
            logger.error(
                "llm_call_failed", error=str(exc), error_type=type(exc).__name__
            )
            raise LLMProviderError(
                "The AI provider failed to respond. Please try again.",
                details={"provider_error": str(exc)},
            ) from exc

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("llm_returned_invalid_json", raw_response=raw[:500])
            raise LLMProviderError(
                "The AI provider returned a malformed response.",
            ) from exc
