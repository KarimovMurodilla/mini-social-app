from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.core.schemas import Base
from src.user.schemas import UserSummaryViewModel


class PostCreate(Base):
    title: str = Field(min_length=5, max_length=255)
    content: str = Field(min_length=1, max_length=10000)


class PostUpdate(Base):
    title: str | None = Field(default=None, min_length=5, max_length=255)
    content: str | None = Field(default=None, min_length=1, max_length=10000)


class LikeViewModel(Base):
    user_id: UUID
    post_id: UUID
    created_at: datetime


class CommentCreate(Base):
    content: str = Field(min_length=1, max_length=2000)


class CommentViewModel(Base):
    id: UUID
    post_id: UUID
    author_id: UUID
    content: str
    created_at: datetime


class PostViewModel(Base):
    id: UUID
    author_id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class PostWithDetailsViewModel(PostViewModel):
    author: UserSummaryViewModel | None = None
    comments: list[CommentViewModel] = []
    likes: list[LikeViewModel] = []

    @property
    def likes_count(self) -> int:
        return len(self.likes)

    @property
    def comments_count(self) -> int:
        return len(self.comments)


class FeedPostViewModel(Base):
    id: UUID
    title: str
    content: str
    likes: list[UUID]  # List of user_uuids who liked


class FeedViewModel(Base):
    username: str
    posts: list[FeedPostViewModel]
