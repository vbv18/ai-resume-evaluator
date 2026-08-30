import uuid
from datetime import datetime, timezone
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.evaluation_run import EvaluationRun
from app.models.evaluation_result import EvaluationResult
from app.repositories.base import BaseRepository


class EvaluationRepository(BaseRepository[EvaluationRun]):
    def __init__(self, session: AsyncSession):
        super().__init__(EvaluationRun, session)

    async def get_with_result(
        self, id: uuid.UUID, user_id: uuid.UUID
    ) -> EvaluationRun | None:
        statement = (
            select(EvaluationRun)
            .where(EvaluationRun.id == id)
            .where(EvaluationRun.user_id == user_id)
            .options(selectinload(EvaluationRun.result))
            .execution_options(populate_existing=True)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_with_result_by_id(self, id: uuid.UUID) -> EvaluationRun | None:
        statement = (
            select(EvaluationRun)
            .where(EvaluationRun.id == id)
            .options(selectinload(EvaluationRun.result))
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_runs_by_user(
        self, user_id: uuid.UUID, *, skip: int = 0, limit: int = 20
    ) -> Sequence[EvaluationRun]:
        statement = (
            select(EvaluationRun)
            .where(EvaluationRun.user_id == user_id)
            .order_by(EvaluationRun.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def list_by_resume_version(
        self, resume_version_id: uuid.UUID, user_id: uuid.UUID
    ) -> Sequence[EvaluationRun]:
        statement = (
            select(EvaluationRun)
            .where(EvaluationRun.resume_version_id == resume_version_id)
            .where(EvaluationRun.user_id == user_id)
            .order_by(EvaluationRun.created_at.desc())
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    # Result Creation
    async def create_result(self, result_instance: EvaluationResult) -> EvaluationResult:
        self.session.add(result_instance)
        await self.session.flush()
        await self.session.refresh(result_instance)
        return result_instance

    # PostgreSQL SKIP LOCKED Job Worker claim query
    async def claim_next_queued_run(self) -> EvaluationRun | None:
        """
        Atomically claims the next QUEUED evaluation run using SELECT FOR UPDATE SKIP LOCKED.
        Guarantees that multiple concurrent workers never process the same job.
        """
        statement = (
            select(EvaluationRun)
            .where(EvaluationRun.status == "QUEUED")
            .order_by(EvaluationRun.created_at.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        )
        result = await self.session.execute(statement)
        run = result.scalar_one_or_none()

        if run is not None:
            run.status = "PROCESSING"
            run.started_at = datetime.now(timezone.utc)
            await self.session.flush()

        return run
