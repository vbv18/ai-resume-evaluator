import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.profile import Profile
    from app.models.resume_version import ResumeVersion


class Resume(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    """
    Logical resume owned by a user.
    """
    __tablename__ = "resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    target_role: Mapped[str | None] = mapped_column(String(150), nullable=True)
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )

    # Relationships
    user: Mapped["Profile"] = relationship("Profile", back_populates="resumes", lazy="selectin")
    versions: Mapped[list["ResumeVersion"]] = relationship(
        "ResumeVersion",
        back_populates="resume",
        cascade="all, delete-orphan",
        order_by="ResumeVersion.version_number.desc()",
        lazy="selectin",
    )
