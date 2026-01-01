from pydantic import Field

from app.core.constants import FieldSizes
from app.schemas import BaseSchema, BaseTimestampSchema


class TopicBase(BaseSchema):
    """Base topic schema"""

    name: str = Field(min_length=1, max_length=FieldSizes.TOPIC_NAME)
    slug: str = Field(min_length=1, max_length=FieldSizes.TOPIC_SLUG)
    description: str | None = None


class TopicCreate(BaseSchema):
    """Topic creation schema"""

    name: str = Field(min_length=1, max_length=FieldSizes.TOPIC_NAME)
    slug: str = Field(min_length=1, max_length=FieldSizes.TOPIC_SLUG)
    description: str | None = None


class TopicUpdate(BaseSchema):
    """Topic update schema"""

    name: str | None = Field(None, min_length=1, max_length=FieldSizes.TOPIC_NAME)
    slug: str | None = Field(None, min_length=1, max_length=FieldSizes.TOPIC_SLUG)
    description: str | None = None
    is_active: bool | None = None


class TopicResponse(BaseTimestampSchema):
    """Topic schema for API response"""

    id: int
    name: str
    slug: str
    description: str | None
    is_active: bool
