import uuid
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.resume import Resume
from app.models.resume_version import ResumeVersion
from app.repositories.base import BaseRepository


class ResumeVersionRepository(BaseRepository[ResumeVersion]):
    def __init__(self, session: AsyncSession):
        super().__init__(ResumeVersion, session)

    async def get_by_version_number(
        self, resume_id: uuid.UUID, version_number: int
    ) -> ResumeVersion | None:
        statement = (
            select(ResumeVersion)
            .where(ResumeVersion.resume_id == resume_id)
            .where(ResumeVersion.version_number == version_number)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_id_and_user(
        self, version_id: uuid.UUID, user_id: uuid.UUID
    ) -> ResumeVersion | None:
        statement = (
            select(ResumeVersion)
            .join(Resume, ResumeVersion.resume_id == Resume.id)
            .where(ResumeVersion.id == version_id)
            .where(Resume.user_id == user_id)
            .where(Resume.is_deleted == False)  # noqa: E712
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_resume(
        self, resume_id: uuid.UUID
    ) -> Sequence[ResumeVersion]:
        statement = (
            select(ResumeVersion)
            .where(ResumeVersion.resume_id == resume_id)
            .order_by(ResumeVersion.version_number.desc())
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_next_version_number(self, resume_id: uuid.UUID) -> int:
        statement = (
            select(func.coalesce(func.max(ResumeVersion.version_number), 0))
            .where(ResumeVersion.resume_id == resume_id)
        )
        result = await self.session.execute(statement)
        max_version = result.scalar_one()
        return max_version + 1
