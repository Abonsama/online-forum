from sqlalchemy import BigInteger, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PostTopic(Base):
    """Junction table for Post-Topic many-to-many relationship"""


    __table_args__ = (
        UniqueConstraint("post_id", "topic_id", name="uq_post_topic_post_id_topic_id"),
        Index("ix_post_topic_topic_id", "topic_id"),
    )

    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("post.id", ondelete="CASCADE"),
        nullable=False,
    )
    topic_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("topic.id", ondelete="CASCADE"),
        nullable=False,
    )
