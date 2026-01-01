from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.junctions.post_vote import PostVote
from app.repos import BaseRepository
from app.schemas import PostVoteCreate, PostVoteUpdate


class PostVoteRepo(BaseRepository[PostVote, PostVoteCreate, PostVoteUpdate]):
    def __init__(self, session: AsyncSession):
        """PostVote repository for database operations"""
        super().__init__(session, PostVote)

    async def get_user_vote(self, user_id: int, post_id: int) -> PostVote | None:
        """
        Get a user's vote on a post

        Args:
            user_id (int): The ID of the user.
            post_id (int): The ID of the post.

        Returns:
            PostVote | None: The vote object if found, else None.
        """
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.post_id == post_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def upsert_vote(
        self,
        user_id: int,
        post_id: int,
        vote_type: int,
    ) -> PostVote | None:
        """
        Insert or update a vote (PostgreSQL upsert)

        Args:
            user_id (int): The ID of the user.
            post_id (int): The ID of the post.
            vote_type (int): The vote type (1 for upvote, -1 for downvote).

        Returns:
            PostVote | None: The created or updated vote object.
        """
        stmt = (
            pg_insert(self.model)
            .values(user_id=user_id, post_id=post_id, vote_type=vote_type)
            .on_conflict_do_update(
                index_elements=["user_id", "post_id"],
                set_={"vote_type": vote_type},
            )
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def remove_vote(self, user_id: int, post_id: int) -> bool:
        """
        Remove a user's vote on a post

        Args:
            user_id (int): The ID of the user.
            post_id (int): The ID of the post.

        Returns:
            bool: True if vote was removed, False otherwise.
        """
        stmt = delete(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.post_id == post_id,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0  # type: ignore

    async def get_post_votes(self, post_id: int) -> list[PostVote]:
        """
        Get all votes for a post

        Args:
            post_id (int): The ID of the post.

        Returns:
            list[PostVote]: List of votes for the post.
        """
        query = select(self.model).where(self.model.post_id == post_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_votes_for_posts(
        self,
        user_id: int,
        post_ids: list[int],
    ) -> dict[int, int]:
        """
        Get user's votes for multiple posts (for feed display)

        Args:
            user_id (int): The ID of the user.
            post_ids (list[int]): List of post IDs.

        Returns:
            dict[int, int]: Dictionary mapping post_id to vote_type.
        """
        if not post_ids:
            return {}

        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.post_id.in_(post_ids),
            )
        )
        result = await self.session.execute(query)
        votes = result.scalars().all()

        return {vote.post_id: vote.vote_type for vote in votes}
