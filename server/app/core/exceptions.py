from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """
    Base class for all expected/handled application errors.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "Internal Error"

    def __init__(self, message: str, *, details: dict | None = None):
        self.message = message
        self.details = details
        super().__init__(message)


class UnsupportedFileTypeError(AppError):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    error_code = "unsupported_file_type"


class FileTooLargeError(AppError):
    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
    error_code = "file_too_large"


class EmptyResumeTextError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "empty_resume_text"


class TokenLimitExceededError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "token_limit_exceeded"


class LLMResponseValidationError(AppError):
    """Raised when the LLM returns JSON that fails Pydantic validation, even after retry."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "llm_response_invalid"


class LLMProviderError(AppError):
    """Raised when the Groq API call itself fails (timeout, rate limit, 5xx, etc.)."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "llm_provider_error"


def register_exception_handlers(app: FastAPI) -> None:
    """
    Central place to map exceptions -> HTTP responses.
    Equivalent of a single Express `app.use((err, req, res, next) => ...)` handler.
    """

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "app_error",
            error_code=exc.error_code,
            message=exc.message,
            path=request.url.path,
            details=exc.details,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "unhandled_exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred.",
                }
            },
        )
