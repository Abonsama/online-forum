from typing import Literal

from sqlalchemy import func, or_, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.junctions.post_topic import PostTopic
from app.models.post import Post
from app.repos import BaseRepository
from app.schemas import PostCreate, PostUpdate


class PostRepo(BaseRepository[Post, PostCreate, PostUpdate]):
    def __init__(self, session: AsyncSession):
        """Post repository for database operations"""
        super().__init__(session, Post)

    async def get_feed(
        self,
        sort: Literal["hot", "new", "top"] = "hot",
        topic_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[Post]:
        """
        Get posts feed with sorting

        Args:
            sort (Literal["hot", "new", "top"]): Sorting method. Defaults to "hot".
            topic_ids (list[int] | None): Filter by topic IDs. None means all topics.
            skip (int): Number of posts to skip for pagination.
            limit (int): Maximum number of posts to return.
            include_deleted (bool): Whether to include deleted posts. Defaults to False.

        Returns:
            list[Post]: List of posts.
        """
        query = select(self.model)

        # Filter by topics if provided
        if topic_ids:
            query = query.join(PostTopic).where(PostTopic.topic_id.in_(topic_ids))

        # Filter out deleted posts unless requested
        if not include_deleted:
            query = query.where(self.model.is_deleted == False)

        # Apply sorting
        if sort == "hot":
            # Hot score: vote_count / (hours_since_posted + 2)^1.5
            hours_since = func.extract("epoch", func.now() - self.model.created_at) / 3600
            hot_score = self.model.vote_count / func.power(hours_since + 2, 1.5)
            query = query.order_by(hot_score.desc())
        elif sort == "new":
            query = query.order_by(self.model.created_at.desc())
        elif sort == "top":
            query = query.order_by(self.model.vote_count.desc())

        # Add secondary sorting by created_at for consistency
        query = query.order_by(self.model.created_at.desc())

        # Pagination
        query = query.offset(skip).limit(limit)

        # Eager load relationships
        query = query.options(
            selectinload(self.model.user),
            selectinload(self.model.topics),
        )

        result = await self.session.execute(query)
        return list(result.scalars().unique().all())

    async def get_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[Post]:
        """
        Get posts by user ID

        Args:
            user_id (int): The ID of the user.
            skip (int): Number of posts to skip for pagination.
            limit (int): Maximum number of posts to return.
            include_deleted (bool): Whether to include deleted posts. Defaults to False.

        Returns:
            list[Post]: List of posts by the user.
        """
        query = select(self.model).where(self.model.user_id == user_id)

        if not include_deleted:
            query = query.where(self.model.is_deleted == False)

        query = query.order_by(self.model.created_at.desc()).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search(
        self,
        search_query: str,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False,
    ) -> list[Post]:
        """
        Search posts by title and content

        Args:
            search_query (str): The search query string.
            skip (int): Number of posts to skip for pagination.
            limit (int): Maximum number of posts to return.
            include_deleted (bool): Whether to include deleted posts. Defaults to False.

        Returns:
            list[Post]: List of matching posts.
        """
        search_pattern = f"%{search_query}%"

        query = select(self.model).where(
            or_(
                self.model.title.ilike(search_pattern),
                self.model.content.ilike(search_pattern),
            )
        )

        if not include_deleted:
            query = query.where(self.model.is_deleted == False)

        # Order by relevance: title matches first, then by vote count
        query = query.order_by(
            self.model.title.ilike(search_pattern).desc(),
            self.model.vote_count.desc(),
            self.model.created_at.desc(),
        )

        query = query.offset(skip).limit(limit)

        # Eager load relationships
        query = query.options(
            selectinload(self.model.user),
            selectinload(self.model.topics),
        )

        result = await self.session.execute(query)
        return list(result.scalars().unique().all())

    async def increment_view_count(self, post_id: int) -> bool:
        """
        Increment view count for a post

        Args:
            post_id (int): The ID of the post.

        Returns:
            bool: True if successful, False otherwise.
        """
        # stmt = text("UPDATE online_forum.post SET view_count = view_count + 1 WHERE id = :post_id")
        stmt = update(self.model).where(self.model.id == post_id).values(
            view_count=self.model.view_count + 1
        )
        result = await self.session.execute(stmt, {"post_id": post_id})
        await self.session.commit()
        return result.rowcount > 0  # type: ignore

    async def increment_comment_count(self, post_id: int, increment: int = 1) -> bool:
        """
        Increment or decrement comment count for a post

        Args:
            post_id (int): The ID of the post.
            increment (int): The amount to increment (positive) or decrement (negative).

        Returns:
            bool: True if successful, False otherwise.
        """
        # stmt = text(
        #     "UPDATE online_forum.post SET comment_count = comment_count + :increment WHERE id = :post_id"
        # )
        stmt = update(self.model).where(self.model.id == post_id).values(
            comment_count=self.model.comment_count + increment
        )
        result = await self.session.execute(stmt, {"post_id": post_id, "increment": increment})
        await self.session.commit()
        return result.rowcount > 0  # type: ignore

    async def update_vote_count(self, post_id: int, new_vote_count: int) -> bool:
        """
        Update vote count for a post (called from application logic)

        Args:
            post_id (int): The ID of the post.
            new_vote_count (int): The new vote count.

        Returns:
            bool: True if successful, False otherwise.
        """
        # stmt = text("UPDATE online_forum.post SET vote_count = :vote_count WHERE id = :post_id")
        stmt = update(self.model).where(self.model.id == post_id).values(vote_count=new_vote_count)
        result = await self.session.execute(
            stmt, {"post_id": post_id, "vote_count": new_vote_count}
        )
        await self.session.commit()
        return result.rowcount > 0  # type: ignore

    async def soft_delete(self, post_id: int) -> bool:
        """
        Soft delete a post by setting is_deleted to True

        Args:
            post_id (int): The ID of the post to soft delete.

        Returns:
            bool: True if successful, False otherwise.
        """
        # stmt = text("UPDATE online_forum.post SET is_deleted = true WHERE id = :post_id")
        stmt = update(self.model).where(self.model.id == post_id).values(is_deleted=True)
        result = await self.session.execute(stmt, {"post_id": post_id})
        await self.session.commit()
        return result.rowcount > 0  # type: ignore

    async def associate_topics(self, post_id: int, topic_ids: list[int]) -> None:
        """
        Associate topics with a post (bulk insert into post_topic junction table)

        Args:
            post_id (int): The ID of the post.
            topic_ids (list[int]): List of topic IDs to associate (1-5 topics).

        Raises:
            ValueError: If topic_ids list is empty or has more than 5 items.
        """
        if not topic_ids or len(topic_ids) < 1 or len(topic_ids) > 5:
            raise ValueError("Must provide between 1 and 5 topic IDs")

        # Bulk insert with ON CONFLICT DO NOTHING to handle duplicates
        values = [{"post_id": post_id, "topic_id": topic_id} for topic_id in topic_ids]

        stmt = text(
            """
            INSERT INTO online_forum.post_topic (post_id, topic_id)
            VALUES (:post_id, :topic_id)
            ON CONFLICT (post_id, topic_id) DO NOTHING
        """
        )

        for value in values:
            await self.session.execute(stmt, value)

        await self.session.commit()

    async def remove_associations(self, post_id: int) -> None:
        """
        Remove all topic associations for a post

        Args:
            post_id (int): The ID of the post.
        """
        stmt = text("DELETE FROM online_forum.post_topic WHERE post_id = :post_id")
        await self.session.execute(stmt, {"post_id": post_id})
        await self.session.commit()
