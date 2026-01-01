from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from app.repos.base import BaseRepository

Model = TypeVar("Model")


class BaseService:
    """
    Base service class providing common utilities for all services.

    Provides standardized error handling and authorization checks
    that are inherited by all service classes.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize base service with database session.

        Args:
            db (AsyncSession): Database session for repository operations.
        """
        self.db = db

    async def _get_or_404(
        self,
        repo: BaseRepository,
        id: int,
        resource_name: str = "Resource",
    ) -> Any:
        """
        Get a resource by ID or raise NotFoundException.

        Args:
            repo (BaseRepository): Repository to fetch from.
            id (int): ID of the resource.
            resource_name (str): Name of the resource for error messages.

        Returns:
            Any: The resource object.

        Raises:
            NotFoundException: If resource doesn't exist.
        """
        resource = await repo.get_by_id(id)
        if not resource:
            raise NotFoundException(detail=f"{resource_name} not found")
        return resource

    def _verify_ownership(
        self,
        item: Any,
        user_id: int,
        resource_name: str = "resource",
    ) -> None:
        """
        Verify that user owns the resource.

        Args:
            item: The resource object (must have user_id attribute).
            user_id (int): ID of the user claiming ownership.
            resource_name (str): Name of the resource for error messages.

        Raises:
            ForbiddenException: If user doesn't own the resource.
        """
        if not hasattr(item, "user_id"):
            raise ValueError(f"{resource_name} does not have user_id attribute")

        if item.user_id != user_id:
            raise ForbiddenException(
                detail=f"You don't have permission to modify this {resource_name}"
            )

    def _verify_moderator_or_owner(
        self,
        item: Any,
        user_id: int,
        user_role: str,
        resource_name: str = "resource",
    ) -> None:
        """
        Verify that user is either the owner or a moderator/admin.

        Args:
            item: The resource object (must have user_id attribute).
            user_id (int): ID of the user.
            user_role (str): Role of the user ('user', 'moderator', 'admin').
            resource_name (str): Name of the resource for error messages.

        Raises:
            ForbiddenException: If user is neither owner nor moderator/admin.
        """
        if not hasattr(item, "user_id"):
            raise ValueError(f"{resource_name} does not have user_id attribute")

        # Allow if user is owner OR moderator/admin
        is_owner = item.user_id == user_id
        is_privileged = user_role in ["moderator", "admin"]

        if not (is_owner or is_privileged):
            raise ForbiddenException(
                detail=f"You don't have permission to modify this {resource_name}"
            )

    def _verify_moderator(self, user_role: str) -> None:
        """
        Verify that user is a moderator or admin.

        Args:
            user_role (str): Role of the user.

        Raises:
            ForbiddenException: If user is not a moderator/admin.
        """
        if user_role not in ["moderator", "admin"]:
            raise ForbiddenException(detail="You don't have permission to perform this action")
