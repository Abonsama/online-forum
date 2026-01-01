from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from app.schemas import BaseSchema, BaseTimestampSchema

ReportableType = Literal["post", "comment"]
ReportReason = Literal["spam", "harassment", "inappropriate", "misinformation", "other"]
ReportStatus = Literal["pending", "resolved", "dismissed"]


class ReportCreate(BaseSchema):
    """Report creation schema"""

    reportable_type: ReportableType
    reportable_id: int
    reason: ReportReason
    details: str | None = Field(None, max_length=500)

    @field_validator("details")
    def validate_details_for_other(cls, value: str | None, info) -> str | None:
        """Require details when reason is 'other'"""
        if info.data.get("reason") == "other" and not value:
            raise ValueError("Details are required when reason is 'other'")
        return value


class ReportUpdate(BaseSchema):
    """Report update schema (for moderator actions)"""

    status: ReportStatus | None = None
    moderator_note: str | None = None


class ReportResponse(BaseTimestampSchema):
    """Report schema for API response"""

    id: int
    reporter_id: int | None
    reportable_type: str
    reportable_id: int
    reason: str
    details: str | None
    status: str
    resolved_by: int | None
    moderator_note: str | None
    resolved_at: datetime | None


class ReportDetailResponse(ReportResponse):
    """Detailed report schema with relationships"""

    from app.schemas.user import UserResponse

    reporter: UserResponse | None = None
    resolver: UserResponse | None = None
