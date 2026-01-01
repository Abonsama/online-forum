from sqlalchemy.ext.asyncio import AsyncSession

from app.repos.comment_vote import CommentVoteRepo
from app.repos.comment import CommentRepo
from app.repos.post_vote import PostVoteRepo
from app.repos.post import PostRepo
from app.services.base_service import BaseService


class VoteService(BaseService):
    """
    Service for voting logic on posts and comments.

    Handles vote creation, updates, removals, and vote count recalculation.
    Implements toggle logic: same vote removes it, different vote updates it.
    """

    def __init__(self, db: AsyncSession):
        """Initialize vote service with database session."""
        super().__init__(db)
        self.post_vote_repo = PostVoteRepo(db)
        self.post_repo = PostRepo(db)
        self.comment_vote_repo = CommentVoteRepo(db)
        self.comment_repo = CommentRepo(db)

    async def vote_on_post(
        self, user_id: int, post_id: int, vote_type: int
    ) -> dict[str, int | None]:
        """
        Vote on a post with toggle logic.

        Logic:
        - If vote_type = 0: Remove vote
        - If existing vote == new vote: Remove vote (toggle off)
        - Otherwise: Create or update vote

        Args:
            user_id (int): ID of the user voting.
            post_id (int): ID of the post.
            vote_type (int): Vote type (1 for upvote, -1 for downvote, 0 to remove).

        Returns:
            dict: {"vote_count": int, "user_vote": int | None}

        Raises:
            NotFoundException: If post doesn't exist.
        """
        # Verify post exists
        await self._get_or_404(self.post_repo, post_id, "Post")

        # Get existing vote
        existing_vote = await self.post_vote_repo.get_user_vote(user_id, post_id)

        # Determine action
        if vote_type == 0:
            # Remove vote explicitly
            if existing_vote:
                await self.post_vote_repo.remove_vote(user_id, post_id)
            user_vote = None
        elif existing_vote and existing_vote.vote_type == vote_type:
            # Toggle off (same vote clicked again)
            await self.post_vote_repo.remove_vote(user_id, post_id)
            user_vote = None
        else:
            # Create or update vote
            await self.post_vote_repo.upsert_vote(user_id, post_id, vote_type)
            user_vote = vote_type

        # Recalculate vote count from all votes
        all_votes = await self.post_vote_repo.get_post_votes(post_id)
        vote_count = sum(v.vote_type for v in all_votes)

        # Update post vote_count
        await self.post_repo.update_vote_count(post_id, vote_count)

        return {
            "vote_count": vote_count,
            "user_vote": user_vote,
        }

    async def vote_on_comment(
        self, user_id: int, comment_id: int, vote_type: int
    ) -> dict[str, int | None]:
        """
        Vote on a comment with toggle logic.

        Logic:
        - If vote_type = 0: Remove vote
        - If existing vote == new vote: Remove vote (toggle off)
        - Otherwise: Create or update vote

        Args:
            user_id (int): ID of the user voting.
            comment_id (int): ID of the comment.
            vote_type (int): Vote type (1 for upvote, -1 for downvote, 0 to remove).

        Returns:
            dict: {"vote_count": int, "user_vote": int | None}

        Raises:
            NotFoundException: If comment doesn't exist.
        """
        # Verify comment exists
        await self._get_or_404(self.comment_repo, comment_id, "Comment")

        # Get existing vote
        existing_vote = await self.comment_vote_repo.get_user_vote(user_id, comment_id)

        # Determine action
        if vote_type == 0:
            # Remove vote explicitly
            if existing_vote:
                await self.comment_vote_repo.remove_vote(user_id, comment_id)
            user_vote = None
        elif existing_vote and existing_vote.vote_type == vote_type:
            # Toggle off (same vote clicked again)
            await self.comment_vote_repo.remove_vote(user_id, comment_id)
            user_vote = None
        else:
            # Create or update vote
            await self.comment_vote_repo.upsert_vote(user_id, comment_id, vote_type)
            user_vote = vote_type

        # Recalculate vote count from all votes
        all_votes = await self.comment_vote_repo.get_comment_votes(comment_id)
        vote_count = sum(v.vote_type for v in all_votes)

        # Update comment vote_count
        await self.comment_repo.update_vote_count(comment_id, vote_count)

        return {
            "vote_count": vote_count,
            "user_vote": user_vote,
        }
