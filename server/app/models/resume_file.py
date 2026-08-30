import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.resume_version import ResumeVersion


class ResumeFile(Base, UUIDPrimaryKeyMixin):
    """
    Physical storage metadata for an uploaded resume file.
    Raw text and structured data belong to ResumeVersion, not here.
    """
    __tablename__ = "resume_files"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    storage_provider: Mapped[str] = mapped_column(
        String(50), default="supabase_storage", nullable=False
    )
    storage_bucket: Mapped[str] = mapped_column(
        String(100), default="resumes", nullable=False
    )
    storage_path: Mapped[str] = mapped_column(
        String(500), unique=True, nullable=False
    )
    original_filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    mime_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger, nullable=False
    )
    sha256_checksum: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    versions: Mapped[list["ResumeVersion"]] = relationship(
        "ResumeVersion", back_populates="resume_file"
    )
