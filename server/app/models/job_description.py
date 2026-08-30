import uuid
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.profile import Profile
    from app.models.job_description_version import JobDescriptionVersion


class JobDescription(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Logical job description container owned by a user.
    """
    __tablename__ = "job_descriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["Profile"] = relationship("Profile", back_populates="job_descriptions", lazy="selectin")
    versions: Mapped[list["JobDescriptionVersion"]] = relationship(
        "JobDescriptionVersion",
        back_populates="job_description",
        cascade="all, delete-orphan",
        order_by="JobDescriptionVersion.version_number.desc()",
        lazy="selectin",
    )
