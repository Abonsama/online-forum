from datetime import datetime
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.junctions.post_topic import PostTopic
from app.models.topic import Topic
from app.repos.topic import TopicRepo
from app.services.base_service import BaseService

from typing import AsyncGenerator, TypedDict


class TopicsWithCount(TypedDict):
    id: int
    name: str
    slug: str
    description: str | None
    is_active: bool
    created_at: datetime | None
    post_count: int


class TopicService(BaseService):
    """
    Service for topic-related business logic.

    Handles topic listing with post counts and topic management.
    """

    def __init__(self, db: AsyncSession):
        """Initialize topic service with database session."""
        super().__init__(db)
        self.topic_repo = TopicRepo(db)

    async def get_all_with_counts(
        self, only_active: bool = True
    ) -> AsyncGenerator[TopicsWithCount, None]:
        """
        Get all topics with post counts.

        Args:
            only_active (bool): Whether to return only active topics.

        Returns:
            list[dict]: List of topics with post_count field.
                Each dict has: id, name, slug, description, is_active, created_at, post_count
        """
        # Build query with LEFT JOIN to count posts
        query = (
            select(
                Topic,
                func.count(PostTopic.post_id).label("post_count"),
            )
            .outerjoin(PostTopic, Topic.id == PostTopic.topic_id)
            .group_by(Topic.id)
        )

        if only_active:
            query = query.where(Topic.is_active == True)

        query = query.order_by(Topic.name)

        result = await self.db.execute(query)
        rows = result.all()

        for topic, post_count in rows:
            topic_dict: TopicsWithCount = {
                "id": topic.id,
                "name": topic.name,
                "slug": topic.slug,
                "description": topic.description,
                "is_active": topic.is_active,
                "created_at": topic.created_at if topic.created_at else None,
                "post_count": post_count,
            }
            yield topic_dict

    async def get_by_id(self, topic_id: int) -> Topic:
        """
        Get topic by ID.

        Args:
            topic_id (int): ID of the topic.

        Returns:
            Topic: The topic object.

        Raises:
            NotFoundException: If topic doesn't exist.
        """
        return await self._get_or_404(self.topic_repo, topic_id, "Topic")

    async def get_by_slug(self, slug: str) -> Topic | None:
        """
        Get topic by slug.

        Args:
            slug (str): Slug of the topic.

        Returns:
            Topic | None: The topic object if found, else None.
        """
        return await self.topic_repo.get_by_slug(slug)
