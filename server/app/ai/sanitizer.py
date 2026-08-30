import tiktoken
from app.core.exceptions import TokenLimitExceededError
from app.core.logging import get_logger
from app.lib.constants import MAX_INPUT_TOKENS

logger = get_logger(__name__)

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


def estimate_tokens(text: str) -> int:
    """Estimates the number of BPE tokens in a string."""
    encoding = _get_encoding()
    if encoding is not None:
        return len(encoding.encode(text))
    return max(1, len(text) // 4)


def ensure_within_limit(text: str, *, max_tokens: int = MAX_INPUT_TOKENS, context: str = "Input") -> int:
    """Pre-flight check raising TokenLimitExceededError if input exceeds max_tokens."""
    token_count = estimate_tokens(text)
    if token_count > max_tokens:
        raise TokenLimitExceededError(
            f"{context} exceeds token limit ({token_count} estimated tokens, maximum is {max_tokens}).",
            details={
                "estimated_tokens": token_count,
                "max_tokens": max_tokens,
                "context": context,
            },
        )
    return token_count


def wrap_with_delimiter(tag_name: str, content: str) -> str:
    """
    Wraps untrusted user content in XML tags to defend against prompt injection.
    """
    cleaned = content.strip()
    return f"<{tag_name}>\n{cleaned}\n</{tag_name}>"
