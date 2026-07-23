import tiktoken
from app.core.exceptions import TokenLimitExceededError
from app.core.logging import get_logger

logger = get_logger(__name__)

# cl100k_base is a close-enough proxy for token counting across most modern LLM
# tokenizers (OpenAI/Groq-hosted Llama models don't expose a public tokenizer,
# so this gives a conservative, consistent estimate rather than an exact count).

_ENCODING = None
_ENCODING_LOAD_FAILED = False


def _get_encoding():
    global _ENCODING, _ENCODING_LOAD_FAILED
    if _ENCODING is not None or _ENCODING_LOAD_FAILED:
        return _ENCODING
    try:
        _ENCODING = tiktoken.get_encoding("cl100k_base")
    except Exception as exc:
        logger.warning("tiktoken_load_failed_using_fallback", error=str(exc))
        _ENCODING_LOAD_FAILED = True
    return _ENCODING


# For now - Fallback heuristic: ~4 chars/token is a reasonable approximation for English text across most BPE tokenizers.


def estimate_tokens(text: str) -> int:
    encoding = _get_encoding()
    if encoding is not None:
        return len(encoding.encode(text))
    return max(1, len(text) // 4)


def ensure_within_limit(text: str, *, max_tokens: int, context: str) -> int:
    token_count = estimate_tokens(text)
    if token_count > max_tokens:
        raise TokenLimitExceededError(
            f"{context} is too long ({token_count} estimated tokens, limit is {max_tokens}).",
            details={
                "estimated_tokens": token_count,
                "max_tokens": max_tokens,
                "context": context,
            },
        )
    return token_count
