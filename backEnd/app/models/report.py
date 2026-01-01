from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import FieldSizes
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Report(Base):
    """Report model for flagging posts or comments"""

    __table_args__ = (
        UniqueConstraint(
            "reporter_id",
            "reportable_type",
            "reportable_id",
            name="uq_report_reporter_reportable",
        ),
        CheckConstraint(
            "reportable_type IN ('post', 'comment')",
            name="ck_report_reportable_type",
        ),
        CheckConstraint(
            "status IN ('pending', 'resolved', 'dismissed')",
            name="ck_report_status",
        ),
        Index("ix_report_reportable", "reportable_type", "reportable_id"),
        Index("ix_report_status", "status"),
        Index("ix_report_resolved_by", "resolved_by"),
    )

    reporter_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
    reportable_type: Mapped[str] = mapped_column(
        String(FieldSizes.REPORT_TYPE),
        nullable=False,
    )
    reportable_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        String(FieldSizes.REPORT_REASON),
        nullable=False,
    )
    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(FieldSizes.REPORT_STATUS),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    resolved_by: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
    moderator_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    reporter: Mapped["User | None"] = relationship(
        "User",
        back_populates="reports",
        foreign_keys=[reporter_id],
    )
    resolver: Mapped["User | None"] = relationship(
        "User",
        back_populates="resolved_reports",
        foreign_keys=[resolved_by],
    )
