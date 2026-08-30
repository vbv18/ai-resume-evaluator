import uuid
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.job_description import JobDescription
from app.models.job_description_version import JobDescriptionVersion
from app.repositories.base import BaseRepository


class JobDescriptionRepository(BaseRepository[JobDescription]):
    def __init__(self, session: AsyncSession):
        super().__init__(JobDescription, session)

    async def get_with_versions(
        self, id: uuid.UUID, user_id: uuid.UUID
    ) -> JobDescription | None:
        statement = (
            select(JobDescription)
            .where(JobDescription.id == id)
            .where(JobDescription.user_id == user_id)
            .where(JobDescription.is_archived == False)  # noqa: E712
            .options(selectinload(JobDescription.versions))
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_active_by_user(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 20
    ) -> Sequence[JobDescription]:
        statement = (
            select(JobDescription)
            .where(JobDescription.user_id == user_id)
            .where(JobDescription.is_archived == False)  # noqa: E712
            .options(selectinload(JobDescription.versions))
            .order_by(JobDescription.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def count_active_by_user(self, user_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(JobDescription)
            .where(JobDescription.user_id == user_id)
            .where(JobDescription.is_archived == False)  # noqa: E712
        )
        result = await self.session.execute(statement)
        return result.scalar_one() or 0

    # JD Version methods
    async def create_version(
        self, version: JobDescriptionVersion
    ) -> JobDescriptionVersion:
        self.session.add(version)
        await self.session.flush()
        await self.session.refresh(version)
        return version

    async def get_version_by_id_and_user(
        self, version_id: uuid.UUID, user_id: uuid.UUID
    ) -> JobDescriptionVersion | None:
        statement = (
            select(JobDescriptionVersion)
            .join(
                JobDescription,
                JobDescriptionVersion.job_description_id == JobDescription.id,
            )
            .where(JobDescriptionVersion.id == version_id)
            .where(JobDescription.user_id == user_id)
            .where(JobDescription.is_archived == False)  # noqa: E712
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_version_by_id(
        self, version_id: uuid.UUID
    ) -> JobDescriptionVersion | None:
        statement = select(JobDescriptionVersion).where(
            JobDescriptionVersion.id == version_id
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
