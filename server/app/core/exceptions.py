import uuid
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """
    Base class for all expected/handled application errors.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, *, details: dict | None = None):
        self.message = message
        self.details = details
        super().__init__(message)


class AuthenticationError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "AUTHENTICATION_REQUIRED"


class InvalidTokenError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "INVALID_TOKEN"


class PermissionDeniedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "PERMISSION_DENIED"


class ResourceNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "RESOURCE_NOT_FOUND"


class ResourceConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "RESOURCE_CONFLICT"


class UnsupportedFileTypeError(AppError):
    status_code = status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    error_code = "UNSUPPORTED_FILE_TYPE"


class FileTooLargeError(AppError):
    status_code = status.HTTP_413_CONTENT_TOO_LARGE
    error_code = "FILE_TOO_LARGE"


class EmptyResumeTextError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    error_code = "EMPTY_RESUME_TEXT"


class TokenLimitExceededError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    error_code = "TOKEN_LIMIT_EXCEEDED"


class RateLimitExceededError(AppError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"


class LLMResponseValidationError(AppError):
    """Raised when the LLM returns JSON that fails Pydantic validation, even after retry."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "LLM_RESPONSE_INVALID"


class LLMProviderError(AppError):
    """Raised when the AI Provider API call itself fails (timeout, rate limit, 5xx, etc.)."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "LLM_PROVIDER_ERROR"


class StorageError(AppError):
    """Raised when Supabase Storage upload or download operations fail."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "STORAGE_ERROR"


class DatabaseError(AppError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "DATABASE_ERROR"


def register_exception_handlers(app: FastAPI) -> None:
    """
    Central place to map exceptions -> standardized JSON responses.
    """

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:8]}")
        logger.warning(
            "app_error",
            error_code=exc.error_code,
            message=exc.message,
            path=request.url.path,
            details=exc.details,
            request_id=request_id,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": request_id,
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:8]}")
        logger.error(
            "unhandled_exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=request.url.path,
            request_id=request_id,
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected internal server error occurred.",
                    "details": None,
                    "request_id": request_id,
                }
            },
        )
