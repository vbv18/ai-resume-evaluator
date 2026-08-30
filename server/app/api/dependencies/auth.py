import uuid
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.db.session import get_db
from app.models.profile import Profile
from app.repositories.profile_repo import ProfileRepository
from app.security.jwt import decode_supabase_jwt


async def get_current_user_id(
    authorization: str | None = Header(None, alias="Authorization"),
) -> uuid.UUID:
    """
    FastAPI dependency extracting the authenticated user UUID from the Bearer JWT.
    """
    if not authorization:
        # For development/local convenience without token provided, fallback or raise
        raise AuthenticationError("Authorization header is missing.")

    payload = decode_supabase_jwt(authorization)
    return uuid.UUID(payload["sub"])


async def get_current_user(
    user_id: uuid.UUID = Depends(get_current_user_id),
    authorization: str = Header(..., alias="Authorization"),
    session: AsyncSession = Depends(get_db),
) -> Profile:
    """
    FastAPI dependency resolving the current authenticated Profile.
    Auto-provisions the profile if it does not yet exist.
    """
    payload = decode_supabase_jwt(authorization)
    email = payload.get("email") or f"user_{str(user_id)[:8]}@example.com"
    metadata = payload.get("user_metadata", {})
    display_name = metadata.get("full_name") or metadata.get("name")
    avatar_url = metadata.get("avatar_url")

    profile_repo = ProfileRepository(session)
    profile = await profile_repo.get_or_create(
        user_id=user_id,
        email=email,
        display_name=display_name,
        avatar_url=avatar_url,
    )
    return profile
