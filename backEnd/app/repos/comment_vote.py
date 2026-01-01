from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.junctions.comment_vote import CommentVote
from app.repos import BaseRepository
from app.schemas import CommentVoteCreate, CommentVoteUpdate


class CommentVoteRepo(BaseRepository[CommentVote, CommentVoteCreate, CommentVoteUpdate]):
    def __init__(self, session: AsyncSession):
        """CommentVote repository for database operations"""
        super().__init__(session, CommentVote)

    async def get_user_vote(self, user_id: int, comment_id: int) -> CommentVote | None:
        """
        Get a user's vote on a comment

        Args:
            user_id (int): The ID of the user.
            comment_id (int): The ID of the comment.

        Returns:
            CommentVote | None: The vote object if found, else None.
        """
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.comment_id == comment_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def upsert_vote(
        self,
        user_id: int,
        comment_id: int,
        vote_type: int,
    ) -> CommentVote | None:
        """
        Insert or update a vote (PostgreSQL upsert)

        Args:
            user_id (int): The ID of the user.
            comment_id (int): The ID of the comment.
            vote_type (int): The vote type (1 for upvote, -1 for downvote).

        Returns:
            CommentVote | None: The created or updated vote object.
        """
        stmt = (
            pg_insert(self.model)
            .values(user_id=user_id, comment_id=comment_id, vote_type=vote_type)
            .on_conflict_do_update(
                index_elements=["user_id", "comment_id"],
                set_={"vote_type": vote_type},
            )
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def remove_vote(self, user_id: int, comment_id: int) -> bool:
        """
        Remove a user's vote on a comment

        Args:
            user_id (int): The ID of the user.
            comment_id (int): The ID of the comment.

        Returns:
            bool: True if vote was removed, False otherwise.
        """
        stmt = delete(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.comment_id == comment_id,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0  # type: ignore

    async def get_comment_votes(self, comment_id: int) -> list[CommentVote]:
        """
        Get all votes for a comment

        Args:
            comment_id (int): The ID of the comment.

        Returns:
            list[CommentVote]: List of votes for the comment.
        """
        query = select(self.model).where(self.model.comment_id == comment_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_votes_for_comments(
        self,
        user_id: int,
        comment_ids: list[int],
    ) -> dict[int, int]:
        """
        Get user's votes for multiple comments (for display)

        Args:
            user_id (int): The ID of the user.
            comment_ids (list[int]): List of comment IDs.

        Returns:
            dict[int, int]: Dictionary mapping comment_id to vote_type.
        """
        if not comment_ids:
            return {}

        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.comment_id.in_(comment_ids),
            )
        )
        result = await self.session.execute(query)
        votes = result.scalars().all()

        return {vote.comment_id: vote.vote_type for vote in votes}
