from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.http_exceptions import ConflictException
from app.models.report import Report
from app.repos.report import ReportRepo
from app.schemas.report import ReportCreate
from app.services.base_service import BaseService
from app.services.cache.base import BaseRedisClient


class ReportService(BaseService):
    """
    Service for content reporting and moderation.

    Handles report creation with duplicate detection (Redis + PostgreSQL),
    report resolution, and moderation workflows.
    """

    def __init__(self, db: AsyncSession):
        """Initialize report service with database session."""
        super().__init__(db)
        self.report_repo = ReportRepo(db)
        self.redis_client = BaseRedisClient()

    async def create_report(
        self,
        reporter_id: int,
        reportable_type: str,
        reportable_id: int,
        reason: str,
        details: str | None = None,
    ) -> Report:
        """
        Create a report with duplicate detection.

        Uses Redis for fast 24-hour duplicate check with PostgreSQL fallback.

        Args:
            reporter_id (int): ID of the user creating the report.
            reportable_type (str): Type of content ('post' or 'comment').
            reportable_id (int): ID of the reported content.
            reason (str): Reason for the report.
            details (str | None): Additional details (required if reason='other').

        Returns:
            Report: The created report object.

        Raises:
            ConflictException: If user already reported this content in last 24 hours.
        """
        duplicate_key = f"report:duplicate:{reporter_id}:{reportable_type}:{reportable_id}"

        # Check Redis cache first (24h window) if available
        if self.redis_client.redis_client:
            try:
                exists = await self.redis_client.redis_client.exists(duplicate_key)
                if exists:
                    raise ConflictException(
                        detail="You can only report this content once per 24 hours"
                    )
            except Exception:
                # If Redis fails, continue to PostgreSQL check
                pass

        # Fallback: Check PostgreSQL if Redis unavailable or to catch edge cases
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        db_duplicate = await self.report_repo.check_duplicate_within_timeframe(
            reporter_id=reporter_id,
            reportable_type=reportable_type,
            reportable_id=reportable_id,
            since=cutoff_time,
        )
        if db_duplicate:
            raise ConflictException(detail="You already reported this content recently")

        # Create report in database (permanent storage)
        report_dict = {
            "reporter_id": reporter_id,
            "reportable_type": reportable_type,
            "reportable_id": reportable_id,
            "reason": reason,
            "details": details,
        }

        # Create using model_dump compatible dict
        from pydantic import create_model

        ReportCreateWithReporter = create_model(
            "ReportCreateWithReporter",
            reporter_id=(int, ...),
            __base__=ReportCreate,
        )
        report_data = ReportCreateWithReporter(**report_dict)  # type: ignore
        report = await self.report_repo.create_one(report_data)  # type: ignore

        # Set Redis flag with 24h TTL (only if Redis available)
        if self.redis_client.redis_client:
            try:
                await self.redis_client.redis_client.setex(duplicate_key, 86400, "1")
            except Exception:
                # If Redis fails, report is still created in PostgreSQL
                pass

        return report

    async def resolve_report(
        self,
        report_id: int,
        resolver_id: int,
        user_role: str,
        status: str,
        moderator_note: str | None = None,
    ) -> Report:
        """
        Resolve a report (moderator/admin only).

        Args:
            report_id (int): ID of the report.
            resolver_id (int): ID of the moderator resolving the report.
            user_role (str): Role of the resolver.
            status (str): New status ('resolved' or 'dismissed').
            moderator_note (str | None): Note from moderator.

        Returns:
            Report: The updated report object.

        Raises:
            NotFoundException: If report doesn't exist.
            ForbiddenException: If user is not a moderator/admin.
        """
        # Verify user is moderator or admin
        self._verify_moderator(user_role)

        # Get report
        report = await self._get_or_404(self.report_repo, report_id, "Report")

        # Update report fields manually since some fields not in schema
        from sqlalchemy import update as sql_update
        from app.models.report import Report as ReportModel

        stmt = (
            sql_update(ReportModel)
            .where(ReportModel.id == report_id)
            .values(
                status=status,
                resolved_by=resolver_id,
                moderator_note=moderator_note,
                resolved_at=datetime.utcnow(),
            )
            .returning(ReportModel)
        )
        result = await self.db.execute(stmt)
        report = result.scalar_one()

        return report

    async def get_pending_reports(self, skip: int = 0, limit: int = 50) -> list[Report]:
        """
        Get all pending reports (moderator/admin view).

        Args:
            skip (int): Pagination offset.
            limit (int): Maximum reports to return.

        Returns:
            list[Report]: List of pending reports.
        """
        return await self.report_repo.get_pending(skip=skip, limit=limit)

    async def get_reports_for_item(self, reportable_type: str, reportable_id: int) -> list[Report]:
        """
        Get all reports for a specific item.

        Args:
            reportable_type (str): Type of content ('post' or 'comment').
            reportable_id (int): ID of the content.

        Returns:
            list[Report]: List of reports for the item.
        """
        return await self.report_repo.get_for_item(
            reportable_type=reportable_type,
            reportable_id=reportable_id,
        )

    async def count_pending_reports(self) -> int:
        """
        Count pending reports.

        Returns:
            int: Number of pending reports.
        """
        return await self.report_repo.count_pending()
