from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models import Comment,User


class CommentVote(Base):
    """Comment vote model (upvote/downvote)"""

    __table_args__ = (
        UniqueConstraint("user_id", "comment_id", name="uq_comment_vote_user_id_comment_id"),
        CheckConstraint("vote_type IN (1, -1)", name="ck_comment_vote_vote_type"),
        Index("ix_comment_vote_comment_id", "comment_id"),
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    comment_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("comment.id", ondelete="CASCADE"),
        nullable=False,
    )
    vote_type: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="comment_votes",
    )
    comment: Mapped["Comment"] = relationship(
        "Comment",
        back_populates="votes",
    )
