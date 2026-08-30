import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import Profile
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[Profile]):
    def __init__(self, session: AsyncSession):
        super().__init__(Profile, session)

    async def get_by_email(self, email: str) -> Profile | None:
        statement = select(Profile).where(Profile.email == email.lower().strip())
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        *,
        user_id: uuid.UUID,
        email: str,
        display_name: str | None = None,
        avatar_url: str | None = None,
    ) -> Profile:
        profile = await self.get_by_id(user_id)
        if profile is not None:
            return profile

        new_profile = Profile(
            id=user_id,
            email=email.lower().strip(),
            display_name=display_name,
            avatar_url=avatar_url,
        )
        return await self.create(new_profile)
