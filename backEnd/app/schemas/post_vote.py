from pydantic import Field, field_validator

from app.schemas import BaseSchema, BaseTimestampSchema


class VoteRequest(BaseSchema):
    """Vote request schema for voting on posts"""

    vote: int = Field(
        description="Vote value: 1 for upvote, -1 for downvote, 0 to remove vote", ge=-1, le=1
    )

    @field_validator("vote")
    def validate_vote(cls, value: int) -> int:
        """Validate vote is -1, 0, or 1"""
        if value not in [-1, 0, 1]:
            raise ValueError("Vote must be -1 (downvote), 0 (remove), or 1 (upvote)")
        return value


class PostVoteCreate(BaseSchema):
    """PostVote creation schema"""

    user_id: int
    post_id: int
    vote_type: int = Field(description="1 for upvote, -1 for downvote")

    @field_validator("vote_type")
    def validate_vote_type(cls, value: int) -> int:
        """Validate vote_type is either 1 or -1"""
        if value not in (1, -1):
            raise ValueError("vote_type must be either 1 (upvote) or -1 (downvote)")
        return value


class PostVoteUpdate(BaseSchema):
    """PostVote update schema"""

    vote_type: int = Field(description="1 for upvote, -1 for downvote")

    @field_validator("vote_type")
    def validate_vote_type(cls, value: int) -> int:
        """Validate vote_type is either 1 or -1"""
        if value not in (1, -1):
            raise ValueError("vote_type must be either 1 (upvote) or -1 (downvote)")
        return value


class PostVoteResponse(BaseTimestampSchema):
    """PostVote schema for API response"""

    id: int
    user_id: int
    post_id: int
    vote_type: int
