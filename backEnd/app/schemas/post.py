from pydantic import Field

from app.core.constants import FieldSizes
from app.schemas import BaseSchema, BaseTimestampSchema


class PostCreate(BaseSchema):
    """Post creation schema"""

    title: str = Field(min_length=5, max_length=FieldSizes.POST_TITLE)
    content: str = Field(min_length=10)
    topic_ids: list[int] = Field(min_length=1, max_length=5, description="1-5 topic IDs required")


class PostUpdate(BaseSchema):
    """Post update schema"""

    title: str | None = Field(None, min_length=5, max_length=FieldSizes.POST_TITLE)
    content: str | None = Field(None, min_length=10)
    topic_ids: list[int] | None = Field(None, min_length=1, max_length=5)


class PostResponse(BaseTimestampSchema):
    """Post schema for API response"""

    id: int
    user_id: int | None
    title: str
    content: str
    vote_count: int
    view_count: int
    comment_count: int
    is_deleted: bool


class PostDetailResponse(PostResponse):
    """Detailed post schema with relationships"""

    from app.schemas.topic import TopicResponse
    from app.schemas.user import UserResponse

    user: UserResponse | None = None
    topics: list[TopicResponse] = []


class PostFeedResponse(BaseSchema):
    """Post feed response with user vote"""

    id: int
    user_id: int | None
    title: str
    content: str
    vote_count: int
    view_count: int
    comment_count: int
    created_at: str
    user_vote: int | None = None  # 1 for upvote, -1 for downvote, None for no vote
