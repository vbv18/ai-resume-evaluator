import uuid
from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.evaluation_run import EvaluationRun


class EvaluationResult(Base, UUIDPrimaryKeyMixin):
    """
    Detailed evaluation findings produced by an evaluation run (1-to-1).
    Hybrid model: normalized parent + structured JSONB breakdown.
    """
    __tablename__ = "evaluation_results"

    evaluation_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("evaluation_runs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Detailed structured feedback (JSONB)
    matched_skills: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )
    missing_skills: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )
    keyword_analysis: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
    )
    ats_findings: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
    )
    strengths: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )
    weaknesses: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )
    recommendations: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=list
    )
    section_breakdowns: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
    )

    # Sanitized AI snapshot + provider telemetry (NO API keys or secrets)
    sanitized_ai_response: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    evaluation_run: Mapped["EvaluationRun"] = relationship(
        "EvaluationRun", back_populates="result", lazy="selectin"
    )
