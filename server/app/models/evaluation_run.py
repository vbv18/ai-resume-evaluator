import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin
from app.lib.constants import CURRENT_PROMPT_VERSION, CURRENT_RUBRIC_VERSION

if TYPE_CHECKING:
    from app.models.profile import Profile
    from app.models.resume_version import ResumeVersion
    from app.models.job_description_version import JobDescriptionVersion
    from app.models.evaluation_result import EvaluationResult


class EvaluationRun(Base, UUIDPrimaryKeyMixin):
    """
    Central immutable evaluation run and PostgreSQL SKIP LOCKED queue entity.
    """
    __tablename__ = "evaluation_runs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("resume_versions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    job_description_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("job_description_versions.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(30), default="QUEUED", nullable=False, index=True
    )  # 'QUEUED', 'PROCESSING', 'COMPLETED', 'FAILED', 'CANCELLED'

    ai_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str] = mapped_column(
        String(50), default=CURRENT_PROMPT_VERSION, nullable=False
    )
    rubric_version: Mapped[str] = mapped_column(
        String(50), default=CURRENT_RUBRIC_VERSION, nullable=False
    )

    # Sub-scores returned by AI (0-100)
    ats_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    job_match_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    skills_match_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    experience_match_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Final overall score calculated deterministically by backend code (0-100)
    overall_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    verdict: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Execution telemetry
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Failure details
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["Profile"] = relationship("Profile", back_populates="evaluation_runs", lazy="selectin")
    resume_version: Mapped["ResumeVersion"] = relationship(
        "ResumeVersion", back_populates="evaluation_runs", lazy="selectin"
    )
    job_description_version: Mapped["JobDescriptionVersion"] = relationship(
        "JobDescriptionVersion", back_populates="evaluation_runs", lazy="selectin"
    )
    result: Mapped["EvaluationResult | None"] = relationship(
        "EvaluationResult",
        back_populates="evaluation_run",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
