from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.post.models import Comment, Like, Post
from src.user.models import User


def build_post(
    *,
    post_id: UUID | None = None,
    author: User | None = None,
    author_id: UUID | None = None,
    title: str = "Test Post Title",
    content: str = "Test post content",
    created_at: datetime | None = None,
) -> Post:
    if not author_id and author:
        author_id = author.id

    post = Post(
        id=post_id or uuid4(),
        author_id=author_id or uuid4(),
        title=title,
        content=content,
        created_at=created_at or datetime.now(timezone.utc),
        updated_at=created_at or datetime.now(timezone.utc),
    )
    if author:
        post.author = author
    return post


def build_comment(
    *,
    comment_id: UUID | None = None,
    post_id: UUID | None = None,
    author_id: UUID | None = None,
    content: str = "Test comment content",
    created_at: datetime | None = None,
) -> Comment:
    return Comment(
        id=comment_id or uuid4(),
        post_id=post_id or uuid4(),
        author_id=author_id or uuid4(),
        content=content,
        created_at=created_at or datetime.now(timezone.utc),
        updated_at=created_at or datetime.now(timezone.utc),
    )


def build_like(
    *,
    user_id: UUID | None = None,
    post_id: UUID | None = None,
    created_at: datetime | None = None,
) -> Like:
    return Like(
        user_id=user_id or uuid4(),
        post_id=post_id or uuid4(),
        created_at=created_at or datetime.now(timezone.utc),
        updated_at=created_at or datetime.now(timezone.utc),
    )
