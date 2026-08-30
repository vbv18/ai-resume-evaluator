import uuid
from typing import Any
import jwt
from jwt.exceptions import InvalidTokenError as PyJWTInvalidTokenError

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, InvalidTokenError
from app.core.logging import get_logger

logger = get_logger(__name__)


def decode_supabase_jwt(token: str) -> dict[str, Any]:
    """
    Decodes and validates a Supabase Auth JWT token.
    Extracts the user `sub` UUID and claims.
    """
    settings = get_settings()

    if not token or not token.strip():
        raise AuthenticationError("Authorization token is missing.")

    # Clean bearer prefix if present
    token_str = token.replace("Bearer ", "").strip()

    try:
        # In production with secret provided, verify signature
        if settings.supabase_jwt_secret:
            payload = jwt.decode(
                token_str,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        else:
            # In dev mode without secret, decode payload with signature check disabled
            payload = jwt.decode(
                token_str,
                options={"verify_signature": False, "verify_aud": False},
            )

        if "sub" not in payload:
            raise InvalidTokenError("JWT token missing 'sub' claim.")

        # Ensure sub is a valid UUID
        try:
            uuid.UUID(payload["sub"])
        except ValueError as exc:
            raise InvalidTokenError(f"Invalid user ID in token: {payload['sub']}") from exc

        return payload

    except PyJWTInvalidTokenError as exc:
        logger.warning("jwt_verification_failed", error=str(exc))
        raise InvalidTokenError(f"Invalid or expired authorization token: {str(exc)}") from exc
    except Exception as exc:
        logger.error("jwt_decode_error", error=str(exc))
        raise AuthenticationError("Could not validate authentication credentials.") from exc
