from typing import Any, Protocol, runtime_checkable
from pydantic import BaseModel


@runtime_checkable
class AIProvider(Protocol):
    """
    Abstract AI Provider Protocol for pluggable LLM backends.
    """

    async def generate_structured(
        self,
        *,
        system_prompt: str,
        user_content: str,
        response_schema: type[BaseModel],
        model: str | None = None,
        temperature: float = 0.1,
    ) -> tuple[BaseModel, dict[str, int]]:
        """
        Executes structured JSON extraction/completion and validates with response_schema.
        Returns: (Validated Pydantic Instance, {"prompt_tokens": int, "completion_tokens": int, "total_tokens": int})
        """
        ...
