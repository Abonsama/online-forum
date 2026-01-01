from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models import CommentVote, Post, User


class Comment(Base):
    """Comment model with nested reply support"""

    __table_args__ = (
        Index("ix_comment_post_created_desc", "post_id", "created_at", postgresql_using="btree"),
        Index("ix_comment_post_vote_desc", "post_id", "vote_count", postgresql_using="btree"),
        Index(
            "ix_comment_post_parent_created",
            "post_id",
            "parent_id",
            "created_at",
            postgresql_using="btree",
        ),
    )

    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("post.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    parent_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("comment.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
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
    depth: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        index=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
    )

    # Relationships
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="comments",
    )
    user: Mapped["User | None"] = relationship(
        "User",
        back_populates="comments",
        foreign_keys=[user_id],
    )
    parent: Mapped["Comment | None"] = relationship(
        "Comment",
        remote_side="Comment.id",
        back_populates="replies",
        foreign_keys=[parent_id],
    )
    replies: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="parent",
        foreign_keys=[parent_id],
    )
    votes: Mapped[list["CommentVote"]] = relationship(
        "CommentVote",
        back_populates="comment",
        cascade="all, delete-orphan",
    )
