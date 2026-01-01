from pydantic import Field

from app.schemas import BaseSchema, BaseTimestampSchema


class CommentCreate(BaseSchema):
    """Comment creation schema"""

    post_id: int
    parent_id: int | None = None
    content: str = Field(min_length=1)


class CommentUpdate(BaseSchema):
    """Comment update schema"""

    content: str | None = Field(None, min_length=1)


class CommentResponse(BaseTimestampSchema):
    """Comment schema for API response"""

    id: int
    post_id: int
    user_id: int | None
    parent_id: int | None
    content: str
    vote_count: int
    depth: int
    is_deleted: bool


class CommentDetailResponse(CommentResponse):
    """Detailed comment schema with user information"""

    user_vote: int | None = None  # 1 for upvote, -1 for downvote, None for no vote


class CommentTreeResponse(BaseSchema):
    """Comment with nested replies"""

    id: int
    post_id: int
    user_id: int | None
    parent_id: int | None
    content: str
    vote_count: int
    depth: int
    is_deleted: bool
    created_at: str
    user_vote: int | None = None
    replies: list["CommentTreeResponse"] = []
