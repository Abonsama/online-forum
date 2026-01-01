from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.topic import Topic
from app.repos import BaseRepository
from app.schemas import TopicCreate, TopicUpdate


class TopicRepo(BaseRepository[Topic, TopicCreate, TopicUpdate]):
    def __init__(self, session: AsyncSession):
        """Topic repository for database operations"""
        super().__init__(session, Topic)

    async def get_all(self, only_active: bool = True) -> list[Topic]:
        """
        Get all topics

        Args:
            only_active (bool): Whether to return only active topics. Defaults to True.

        Returns:
            list[Topic]: List of all topics.
        """
        query = select(self.model)

        if only_active:
            query = query.where(self.model.is_active == True)

        query = query.order_by(self.model.name)
        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> Topic | None:
        """
        Get a topic by slug

        Args:
            slug (str): The slug of the topic.

        Returns:
            Topic | None: The topic object if found, else None.
        """
        query = select(self.model).where(self.model.slug == slug)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Topic | None:
        """
        Get a topic by name

        Args:
            name (str): The name of the topic.

        Returns:
            Topic | None: The topic object if found, else None.
        """
        query = select(self.model).where(self.model.name == name)
        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def get_by_name_or_slug(self, name: str, slug: str) -> Topic | None:
        """
        Get a topic by name or slug

        Args:
            identifier (str): The name or slug of the topic.

        Returns:
            Topic | None: The topic object if found, else None.
        """
        query = select(self.model).where(or_(self.model.name == name, self.model.slug == slug))
        result = await self.session.execute(query)

        return result.scalars().first()
