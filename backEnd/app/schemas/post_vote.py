from pydantic import Field, field_validator

from app.schemas import BaseSchema, BaseTimestampSchema


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
