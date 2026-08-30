import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.resume import Resume
    from app.models.job_description import JobDescription
    from app.models.evaluation_run import EvaluationRun


class Profile(Base, TimestampMixin):
    """
    Application-specific user profile associated with Supabase auth.users.id.
    """
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    professional_title: Mapped[str | None] = mapped_column(String(150), nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships (with lazy="selectin" for async SQLAlchemy safety)
    resumes: Mapped[list["Resume"]] = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    job_descriptions: Mapped[list["JobDescription"]] = relationship(
        "JobDescription", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    evaluation_runs: Mapped[list["EvaluationRun"]] = relationship(
        "EvaluationRun", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
