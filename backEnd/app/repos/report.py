from datetime import datetime

from sqlalchemy import and_, select, text, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.report import Report
from app.repos import BaseRepository
from app.schemas import ReportCreate, ReportUpdate


class ReportRepo(BaseRepository[Report, ReportCreate, ReportUpdate]):
    def __init__(self, session: AsyncSession):
        """Report repository for database operations"""
        super().__init__(session, Report)

    async def check_duplicate(
        self,
        reporter_id: int,
        reportable_type: str,
        reportable_id: int,
    ) -> Report | None:
        """
        Check if user already reported this item

        Args:
            reporter_id (int): The ID of the reporter.
            reportable_type (str): The type of reportable ('post' or 'comment').
            reportable_id (int): The ID of the reportable item.

        Returns:
            Report | None: Existing report if found, else None.
        """
        query = select(self.model).where(
            and_(
                self.model.reporter_id == reporter_id,
                self.model.reportable_type == reportable_type,
                self.model.reportable_id == reportable_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def check_duplicate_within_timeframe(
        self,
        reporter_id: int,
        reportable_type: str,
        reportable_id: int,
        since: datetime,
    ) -> Report | None:
        """
        Check if user reported this item within a specific timeframe

        Args:
            reporter_id (int): The ID of the reporter.
            reportable_type (str): The type of reportable ('post' or 'comment').
            reportable_id (int): The ID of the reportable item.
            since (datetime): Check for reports created after this time.

        Returns:
            Report | None: Existing report if found, else None.
        """
        query = select(self.model).where(
            and_(
                self.model.reporter_id == reporter_id,
                self.model.reportable_type == reportable_type,
                self.model.reportable_id == reportable_id,
                self.model.created_at >= since,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_status(
        self,
        status: str = "pending",
        skip: int = 0,
        limit: int = 50,
    ) -> list[Report]:
        """
        Get reports by status

        Args:
            status (str): Report status ('pending', 'resolved', 'dismissed').
            skip (int): Number of reports to skip for pagination.
            limit (int): Maximum number of reports to return.

        Returns:
            list[Report]: List of reports with the specified status.
        """
        query = (
            select(self.model)
            .where(self.model.status == status)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Eager load reporter relationship
        query = query.options(
            selectinload(self.model.reporter),
            selectinload(self.model.resolver),
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending(self, skip: int = 0, limit: int = 50) -> list[Report]:
        """
        Get all pending reports

        Args:
            skip (int): Number of reports to skip for pagination.
            limit (int): Maximum number of reports to return.

        Returns:
            list[Report]: List of pending reports.
        """
        return await self.get_by_status("pending", skip, limit)

    async def get_for_item(
        self,
        reportable_type: str,
        reportable_id: int,
    ) -> list[Report]:
        """
        Get all reports for a specific item (post or comment)

        Args:
            reportable_type (str): The type of reportable ('post' or 'comment').
            reportable_id (int): The ID of the reportable item.

        Returns:
            list[Report]: List of reports for the item.
        """
        query = (
            select(self.model)
            .where(
                and_(
                    self.model.reportable_type == reportable_type,
                    self.model.reportable_id == reportable_id,
                )
            )
            .order_by(self.model.created_at.desc())
        )

        # Eager load reporter relationship
        query = query.options(
            selectinload(self.model.reporter),
            selectinload(self.model.resolver),
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def resolve_report(
        self,
        report_id: int,
        resolver_id: int,
        status: str = "resolved",
        moderator_note: str | None = None,
    ) -> Report | None:
        """
        Resolve a report

        Args:
            report_id (int): The ID of the report.
            resolver_id (int): The ID of the moderator resolving the report.
            status (str): New status ('resolved' or 'dismissed').
            moderator_note (str | None): Optional note from moderator.

        Returns:
            Report | None: The updated report if found, else None.
        """
        stmt = text(
            """
            UPDATE report
            SET status = :status,
                resolved_by = :resolver_id,
                resolved_at = :resolved_at,
                moderator_note = :moderator_note
            WHERE id = :report_id
            RETURNING *
            """
        )

        result = await self.session.execute(
            stmt,
            {
                "report_id": report_id,
                "status": status,
                "resolver_id": resolver_id,
                "resolved_at": datetime.utcnow(),
                "moderator_note": moderator_note,
            },
        )
        await self.session.commit()

        row = result.fetchone()
        if row:
            return self.model(**dict(row._mapping))
        return None

    async def get_by_reporter(
        self,
        reporter_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Report]:
        """
        Get reports submitted by a specific user

        Args:
            reporter_id (int): The ID of the reporter.
            skip (int): Number of reports to skip for pagination.
            limit (int): Maximum number of reports to return.

        Returns:
            list[Report]: List of reports by the user.
        """
        query = (
            select(self.model)
            .where(self.model.reporter_id == reporter_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_pending(self) -> int:
        """
        Count total pending reports

        Returns:
            int: Number of pending reports.
        """
        # stmt = text("SELECT COUNT(*) FROM online_forum.report WHERE status = 'pending'")
        stmt = select(func.count(self.model.id)).where(self.model.status == 'pending')
        result = await self.session.execute(stmt)
        count = result.scalar()
        return count or 0
