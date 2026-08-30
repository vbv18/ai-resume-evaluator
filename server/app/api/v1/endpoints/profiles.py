from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.services import get_profile_repo
from app.models.profile import Profile
from app.repositories.profile_repo import ProfileRepository
from app.schemas.profile import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def get_profile(current_user: Profile = Depends(get_current_user)) -> ProfileResponse:
    """Returns the authenticated user's profile."""
    return ProfileResponse.model_validate(current_user)


@router.patch("", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
async def update_profile(
    payload: ProfileUpdate,
    current_user: Profile = Depends(get_current_user),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
) -> ProfileResponse:
    """Updates profile attributes for the current user."""
    updated = await profile_repo.update(
        current_user,
        display_name=payload.display_name,
        avatar_url=payload.avatar_url,
        professional_title=payload.professional_title,
        onboarding_completed=payload.onboarding_completed,
    )
    return ProfileResponse.model_validate(updated)
