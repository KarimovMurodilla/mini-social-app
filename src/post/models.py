from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.base import Base
from src.core.database.mixins import TimestampMixin, UUIDIDMixin

if TYPE_CHECKING:
    from src.user.models import User


class Post(Base, UUIDIDMixin, TimestampMixin):
    __tablename__ = "posts"

    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    author: Mapped["User"] = relationship(
        "User", back_populates="posts", lazy="selectin"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="post", lazy="selectin", cascade="all, delete-orphan"
    )
    likes: Mapped[list["Like"]] = relationship(
        "Like", back_populates="post", lazy="selectin", cascade="all, delete-orphan"
    )


class Comment(Base, UUIDIDMixin, TimestampMixin):
    __tablename__ = "comments"

    post_id: Mapped[UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(String(2000), nullable=False)

    # Relationships
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    author: Mapped["User"] = relationship("User", lazy="selectin")


class Like(Base, TimestampMixin):
    __tablename__ = "likes"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    post_id: Mapped[UUID] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_user_post_like"),)

    # Relationships
    user: Mapped["User"] = relationship("User", lazy="selectin")
    post: Mapped["Post"] = relationship("Post", back_populates="likes")
