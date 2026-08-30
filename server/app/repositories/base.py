import uuid
from typing import Any, Generic, Sequence, TypeVar
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic Base Repository encapsulating async SQLAlchemy 2.0 CRUD queries.
    Enforces object-level tenant isolation via explicit user_id filters.
    """

    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: uuid.UUID | str) -> ModelType | None:
        target_id = uuid.UUID(str(id)) if not isinstance(id, uuid.UUID) else id
        statement = select(self.model).where(self.model.id == target_id)  # type: ignore
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_id_and_user(
        self, id: uuid.UUID | str, user_id: uuid.UUID | str
    ) -> ModelType | None:
        target_id = uuid.UUID(str(id)) if not isinstance(id, uuid.UUID) else id
        target_user_id = (
            uuid.UUID(str(user_id)) if not isinstance(user_id, uuid.UUID) else user_id
        )
        statement = (
            select(self.model)
            .where(self.model.id == target_id)  # type: ignore
            .where(self.model.user_id == target_user_id)  # type: ignore
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[ModelType]:
        statement = (
            select(self.model)
            .where(self.model.user_id == user_id)  # type: ignore
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def count_by_user(self, user_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(self.model)
            .where(self.model.user_id == user_id)  # type: ignore
        )
        result = await self.session.execute(statement)
        return result.scalar_one() or 0

    async def create(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelType, **kwargs: Any) -> ModelType:
        for key, value in kwargs.items():
            if hasattr(instance, key) and value is not None:
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.flush()
