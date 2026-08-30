import uuid
from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.resume import Resume
    from app.models.resume_file import ResumeFile
    from app.models.evaluation_run import EvaluationRun


class ResumeVersion(Base, UUIDPrimaryKeyMixin):
    """
    Immutable snapshot of a resume version.
    """
    __tablename__ = "resume_versions"
    __table_args__ = (
        UniqueConstraint("resume_id", "version_number", name="uq_resume_version_number"),
    )

    resume_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    input_source: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # 'FILE_UPLOAD', 'URL_IMPORT', 'DIRECT_TEXT'
    resume_file_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("resume_files.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    structured_data: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
    )
    parsing_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
    )
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    resume: Mapped["Resume"] = relationship("Resume", back_populates="versions", lazy="selectin")
    resume_file: Mapped["ResumeFile | None"] = relationship(
        "ResumeFile", back_populates="versions", lazy="selectin"
    )
    evaluation_runs: Mapped[list["EvaluationRun"]] = relationship(
        "EvaluationRun", back_populates="resume_version", lazy="selectin"
    )
