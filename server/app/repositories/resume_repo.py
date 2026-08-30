import uuid
from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.resume import Resume
from app.models.resume_file import ResumeFile
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    def __init__(self, session: AsyncSession):
        super().__init__(Resume, session)

    async def get_with_versions(self, id: uuid.UUID, user_id: uuid.UUID) -> Resume | None:
        statement = (
            select(Resume)
            .where(Resume.id == id)
            .where(Resume.user_id == user_id)
            .where(Resume.is_deleted == False)  # noqa: E712
            .options(selectinload(Resume.versions))
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_active_by_user(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 20
    ) -> Sequence[Resume]:
        statement = (
            select(Resume)
            .where(Resume.user_id == user_id)
            .where(Resume.is_deleted == False)  # noqa: E712
            .options(selectinload(Resume.versions))
            .order_by(Resume.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def count_active_by_user(self, user_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Resume)
            .where(Resume.user_id == user_id)
            .where(Resume.is_deleted == False)  # noqa: E712
        )
        result = await self.session.execute(statement)
        return result.scalar_one() or 0

    async def soft_delete(self, resume: Resume) -> None:
        resume.is_deleted = True
        resume.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()

    # File metadata methods
    async def create_file(self, file_record: ResumeFile) -> ResumeFile:
        self.session.add(file_record)
        await self.session.flush()
        await self.session.refresh(file_record)
        return file_record

    async def get_file_by_id_and_user(
        self, file_id: uuid.UUID, user_id: uuid.UUID
    ) -> ResumeFile | None:
        statement = (
            select(ResumeFile)
            .where(ResumeFile.id == file_id)
            .where(ResumeFile.user_id == user_id)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()
