from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import FieldSizes
from app.models.base import Base
from app.models.junctions.post_topic import PostTopic

if TYPE_CHECKING:
    from app.models import Comment, PostVote, Topic, User


class Post(Base):
    """Post model"""

    __table_args__ = (
        Index("ix_post_created_at_desc", "created_at", postgresql_using="btree"),
        Index("ix_post_vote_count_desc", "vote_count", postgresql_using="btree"),
        Index(
            "ix_post_hot_score",
            "vote_count",
            "created_at",
            postgresql_using="btree",
        ),
    )

    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(FieldSizes.POST_TITLE),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    vote_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    view_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    comment_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
    )

    # Relationships
    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="posts",
        foreign_keys=[user_id],
    )
    topics: Mapped[list["Topic"]] = relationship(
        "Topic",
        secondary=lambda: PostTopic.__table__,
        back_populates="posts",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete-orphan",
    )
    votes: Mapped[list["PostVote"]] = relationship(
        "PostVote",
        back_populates="post",
        cascade="all, delete-orphan",
    )
