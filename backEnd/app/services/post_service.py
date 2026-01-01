from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions.http_exceptions import BadRequestException
from app.models.post import Post
from app.repos.post import PostRepo
from app.repos.post_vote import PostVoteRepo
from app.repos.topic import TopicRepo
from app.schemas.post import PostCreate, PostUpdate
from app.services.base_service import BaseService


class PostService(BaseService):
    """
    Service for post-related business logic.

    Handles post CRUD operations, topic validation and association,
    ownership verification, and authorization checks.
    """

    def __init__(self, db: AsyncSession):
        """Initialize post service with database session."""
        super().__init__(db)
        self.post_repo = PostRepo(db)
        self.topic_repo = TopicRepo(db)
        self.vote_repo = PostVoteRepo(db)

    async def create_post(self, user_id: int, data: PostCreate) -> Post:
        """
        Create a new post with topic associations.

        Args:
            user_id (int): ID of the user creating the post.
            data (PostCreate): Post creation data with title, content, and topic_ids.

        Returns:
            Post: The created post object.

        Raises:
            BadRequestException: If topic IDs are invalid.
        """
        # Validate that all topics exist
        topics = await self.topic_repo.get_all_by_ids(data.topic_ids)
        if len(topics) != len(data.topic_ids):
            found_ids = {t.id for t in topics}
            missing_ids = [tid for tid in data.topic_ids if tid not in found_ids]
            raise BadRequestException(detail=f"Topics with IDs {missing_ids} not found")

        # Create post
        post_data = PostCreate(
            title=data.title,
            content=data.content,
            topic_ids=data.topic_ids,
        )
        # Use model_dump to convert schema to dict, excluding topic_ids
        post_dict = post_data.model_dump(exclude={"topic_ids"})
        post_dict["user_id"] = user_id

        # Create the post using repository's create method
        from pydantic import create_model

        # Create a dynamic schema without topic_ids for repository
        PostCreateRepo = create_model(
            "PostCreateRepo",
            title=(str, ...),
            content=(str, ...),
            user_id=(int, ...),
            __base__=PostCreate.__bases__[0],
        )
        repo_data = PostCreateRepo(**post_dict)  # type: ignore
        post = await self.post_repo.create_one(repo_data)  # type: ignore

        # Associate topics
        await self.post_repo.associate_topics(post.id, data.topic_ids)

        # Refresh to get relationships
        await self.db.refresh(post)

        return post

    async def update_post(self, post_id: int, user_id: int, data: PostUpdate) -> Post:
        """
        Update a post (owner only).

        Args:
            post_id (int): ID of the post to update.
            user_id (int): ID of the user updating the post.
            data (PostUpdate): Updated post data.

        Returns:
            Post: The updated post object.

        Raises:
            NotFoundException: If post doesn't exist.
            ForbiddenException: If user doesn't own the post.
            BadRequestException: If topic IDs are invalid.
        """
        # Get post and verify ownership
        post = await self._get_or_404(self.post_repo, post_id, "Post")
        self._verify_ownership(post, user_id, "post")

        # If updating topics, validate them
        if data.topic_ids is not None:
            topics = await self.topic_repo.get_all_by_ids(data.topic_ids)
            if len(topics) != len(data.topic_ids):
                found_ids = {t.id for t in topics}
                missing_ids = [tid for tid in data.topic_ids if tid not in found_ids]
                raise BadRequestException(detail=f"Topics with IDs {missing_ids} not found")

            # Remove old associations and add new ones
            await self.post_repo.remove_associations(post_id)
            await self.post_repo.associate_topics(post_id, data.topic_ids)

        # Update post fields
        update_data = data.model_dump(exclude_none=True, exclude={"topic_ids"})
        if update_data:
            updated_post = await self.post_repo.update_by_id(post_id, PostUpdate(**update_data))
            if updated_post:
                post = updated_post

        # Refresh to get updated relationships
        await self.db.refresh(post)

        return post

    async def delete_post(self, post_id: int, user_id: int, user_role: str) -> None:
        """
        Delete a post (soft delete - owner or moderator/admin).

        Args:
            post_id (int): ID of the post to delete.
            user_id (int): ID of the user deleting the post.
            user_role (str): Role of the user.

        Raises:
            NotFoundException: If post doesn't exist.
            ForbiddenException: If user is neither owner nor moderator.
        """
        # Get post and verify owner or moderator
        post = await self._get_or_404(self.post_repo, post_id, "Post")
        self._verify_moderator_or_owner(post, user_id, user_role, "post")

        # Soft delete
        await self.post_repo.soft_delete(post_id)

    async def get_post_detail(self, post_id: int) -> Post:
        """
        Get detailed post information with relationships.

        Args:
            post_id (int): ID of the post.

        Returns:
            Post: The post object with user and topics loaded.

        Raises:
            NotFoundException: If post doesn't exist.
        """
        post = await self._get_or_404(self.post_repo, post_id, "Post")

        # Ensure relationships are loaded
        await self.db.refresh(post, ["user", "topics"])

        return post

    async def get_feed(
        self,
        sort: Literal["hot", "new", "top"] = "hot",
        topic_ids: list[int] | None = None,
        skip: int = 0,
        limit: int = 20,
        current_user_id: int | None = None,
    ) -> list[Post]:
        """
        Get posts feed with sorting and optional user votes.

        Args:
            sort (Literal["hot", "new", "top"]): Sorting method.
            topic_ids (list[int] | None): Filter by topic IDs.
            skip (int): Pagination offset.
            limit (int): Maximum posts to return.
            current_user_id (int | None): ID of current user (for user_vote field).

        Returns:
            list[Post]: List of posts with user and topics loaded.
        """
        # Get posts from repository
        posts = await self.post_repo.get_feed(
            sort=sort,
            topic_ids=topic_ids,
            skip=skip,
            limit=limit,
            include_deleted=False,
        )

        # If user is authenticated, add user_vote to each post
        if current_user_id and posts:
            post_ids = [p.id for p in posts]
            vote_map = await self.vote_repo.get_user_votes_for_posts(
                user_id=current_user_id,
                post_ids=post_ids,
            )

            # Add user_vote as dynamic attribute
            for post in posts:
                post.user_vote = vote_map.get(post.id)  # type: ignore

        return posts

    async def search_posts(
        self,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Post]:
        """
        Search posts by title and content.

        Args:
            query (str): Search query string.
            skip (int): Pagination offset.
            limit (int): Maximum posts to return.

        Returns:
            list[Post]: List of matching posts.
        """
        return await self.post_repo.search(
            search_query=query,
            skip=skip,
            limit=limit,
            include_deleted=False,
        )

    async def increment_view_count(self, post_id: int) -> None:
        """
        Increment view count for a post.

        Args:
            post_id (int): ID of the post.
        """
        await self.post_repo.increment_view_count(post_id)
