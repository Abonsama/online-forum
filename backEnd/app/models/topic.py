from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import FieldSizes
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.post import Post


class Topic(Base):
    """Topic model for categorizing posts"""

    name: Mapped[str] = mapped_column(
        String(FieldSizes.TOPIC_NAME),
        unique=True,
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(FieldSizes.TOPIC_SLUG),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

    # Relationships
    posts: Mapped[list["Post"]] = relationship(
        "Post",
        secondary="post_topic",
        back_populates="topics",
    )
