from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment
from app.repos import BaseRepository
from app.schemas import CommentCreate, CommentUpdate


class CommentRepo(BaseRepository[Comment, CommentCreate, CommentUpdate]):
    def __init__(self, session: AsyncSession):
        """Comment repository for database operations"""
        super().__init__(session, Comment)

    async def get_by_post(
        self,
        post_id: int,
        sort: str = "new",
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[Comment]:
        """
        Get comments for a post

        Args:
            post_id (int): The ID of the post.
            sort (str): Sorting method ("new", "old", "best"). Defaults to "new".
            skip (int): Number of comments to skip for pagination.
            limit (int): Maximum number of comments to return.
            include_deleted (bool): Whether to include deleted comments. Defaults to False.

        Returns:
            list[Comment]: List of comments for the post.
        """
        query = select(self.model).where(self.model.post_id == post_id)

        if not include_deleted:
            query = query.where(self.model.is_deleted == False)

        # Apply sorting
        if sort == "best":
            query = query.order_by(self.model.vote_count.desc())
        elif sort == "old":
            query = query.order_by(self.model.created_at.asc())
        else:  # "new"
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(skip).limit(limit)

        # Eager load user relationship
        query = query.options(selectinload(self.model.user))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_replies(
        self,
        parent_id: int,
        sort: str = "new",
        include_deleted: bool = False,
    ) -> list[Comment]:
        """
        Get replies to a comment

        Args:
            parent_id (int): The ID of the parent comment.
            sort (str): Sorting method ("new", "old", "best"). Defaults to "new".
            include_deleted (bool): Whether to include deleted comments. Defaults to False.

        Returns:
            list[Comment]: List of reply comments.
        """
        query = select(self.model).where(self.model.parent_id == parent_id)

        if not include_deleted:
            query = query.where(self.model.is_deleted == False)

        # Apply sorting
        if sort == "best":
            query = query.order_by(self.model.vote_count.desc())
        elif sort == "old":
            query = query.order_by(self.model.created_at.asc())
        else:  # "new"
            query = query.order_by(self.model.created_at.desc())

        # Eager load user relationship
        query = query.options(selectinload(self.model.user))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_top_level_comments(
        self,
        post_id: int,
        sort: str = "new",
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> list[Comment]:
        """
        Get only top-level comments (no parent) for a post

        Args:
            post_id (int): The ID of the post.
            sort (str): Sorting method ("new", "old", "best"). Defaults to "new".
            skip (int): Number of comments to skip for pagination.
            limit (int): Maximum number of comments to return.
            include_deleted (bool): Whether to include deleted comments. Defaults to False.

        Returns:
            list[Comment]: List of top-level comments.
        """
        query = select(self.model).where(
            and_(
                self.model.post_id == post_id,
                self.model.parent_id.is_(None),
            )
        )

        if not include_deleted:
            query = query.where(self.model.is_deleted == False)

        # Apply sorting
        if sort == "best":
            query = query.order_by(self.model.vote_count.desc())
        elif sort == "old":
            query = query.order_by(self.model.created_at.asc())
        else:  # "new"
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(skip).limit(limit)

        # Eager load user relationship
        query = query.options(selectinload(self.model.user))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
    ) -> list[Comment]:
        """
        Get comments by user ID

        Args:
            user_id (int): The ID of the user.
            skip (int): Number of comments to skip for pagination.
            limit (int): Maximum number of comments to return.
            include_deleted (bool): Whether to include deleted comments. Defaults to False.

        Returns:
            list[Comment]: List of comments by the user.
        """
        query = select(self.model).where(self.model.user_id == user_id)

        if not include_deleted:
            query = query.where(self.model.is_deleted == False)

        query = query.order_by(self.model.created_at.desc()).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_vote_count(self, comment_id: int, new_vote_count: int) -> bool:
        """
        Update vote count for a comment (called from application logic)

        Args:
            comment_id (int): The ID of the comment.
            new_vote_count (int): The new vote count.

        Returns:
            bool: True if successful, False otherwise.
        """
        stmt = text(
            "UPDATE online_forum.comment SET vote_count = :vote_count WHERE id = :comment_id"
        )
        result = await self.session.execute(
            stmt, {"comment_id": comment_id, "vote_count": new_vote_count}
        )
        await self.session.commit()
        return result.rowcount > 0  # type: ignore

    async def soft_delete(self, comment_id: int) -> bool:
        """
        Soft delete a comment by setting is_deleted to True

        Args:
            comment_id (int): The ID of the comment to soft delete.

        Returns:
            bool: True if successful, False otherwise.
        """
        stmt = text("UPDATE online_forum.comment SET is_deleted = true WHERE id = :comment_id")
        result = await self.session.execute(stmt, {"comment_id": comment_id})
        await self.session.commit()
        return result.rowcount > 0  # type: ignore

    async def validate_depth(self, parent_id: int | None, max_depth: int = 5) -> tuple[bool, int]:
        """
        Validate if adding a reply would exceed max depth

        Args:
            parent_id (int | None): The ID of the parent comment. None for top-level.
            max_depth (int): Maximum allowed depth. Defaults to 5.

        Returns:
            tuple[bool, int]: (is_valid, depth) - True if depth is valid, and the calculated depth.
        """
        if parent_id is None:
            return (True, 0)

        parent = await self.get_by_id(parent_id)
        if not parent:
            return (False, -1)

        new_depth = parent.depth + 1
        is_valid = new_depth <= max_depth

        return (is_valid, new_depth)
