from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Index, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.user import User


class PostVote(Base):
    """Post vote model (upvote/downvote)"""


    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_post_vote_user_id_post_id"),
        CheckConstraint("vote_type IN (1, -1)", name="ck_post_vote_vote_type"),
        Index("ix_post_vote_post_id", "post_id"),
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("post.id", ondelete="CASCADE"),
        nullable=False,
    )
    vote_type: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="post_votes",
    )
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="votes",
    )
