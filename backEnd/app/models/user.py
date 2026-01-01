from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import FieldSizes
from app.models.base import Base

if TYPE_CHECKING:
    from app.models import Comment, CommentVote, Post, PostVote, Report


class UserRoleEnum(StrEnum):
    """User roles enumeration"""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class User(Base):
    """User model"""

    username: Mapped[str] = mapped_column(
        String(FieldSizes.USERNAME),
        unique=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(FieldSizes.EMAIL),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(FieldSizes.PASSWORD_HASH),
        nullable=False,
    )
    role: Mapped[UserRoleEnum] = mapped_column(
        String(FieldSizes.USER_ROLE),
        nullable=False,
        default="user",
        server_default="user",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Relationships
    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="user",
        foreign_keys="Post.user_id",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="user",
        foreign_keys="Comment.user_id",
    )
    post_votes: Mapped[list["PostVote"]] = relationship(
        "PostVote",
        back_populates="user",
    )
    comment_votes: Mapped[list["CommentVote"]] = relationship(
        "CommentVote",
        back_populates="user",
    )
    reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="reporter",
        foreign_keys="Report.reporter_id",
    )
    resolved_reports: Mapped[list["Report"]] = relationship(
        "Report",
        back_populates="resolver",
        foreign_keys="Report.resolved_by",
    )
