from unittest.mock import AsyncMock

import pytest

from src.core.errors.exceptions import (
    PermissionDeniedException,
)
from src.post.models import Comment, Like, Post
from src.post.schemas import CommentCreate
from src.post.usecases.interaction_usecases import (
    CreateCommentUseCase,
    DeleteCommentUseCase,
    ToggleLikeUseCase,
)
from tests.factories.post_factory import build_comment, build_like, build_post
from tests.factories.user_factory import build_user
from tests.fakes.db import FakeAsyncSession, FakeUnitOfWork


class FakePostsRepository:
    def __init__(self, post: Post | None = None) -> None:
        self._post = post
        self.get_single = AsyncMock(return_value=self._post)


class FakeCommentsRepository:
    def __init__(self, comment: Comment | None = None) -> None:
        self._comment = comment
        self.create = AsyncMock(return_value=self._comment)
        self.get_single = AsyncMock(return_value=self._comment)
        self.delete = AsyncMock()


class FakeLikesRepository:
    def __init__(self, like: Like | None = None) -> None:
        self._like = like
        self.create = AsyncMock(return_value=self._like)
        self.get_single = AsyncMock(return_value=self._like)
        self.delete = AsyncMock()


def build_uow(
    session: FakeAsyncSession,
    posts_repo: FakePostsRepository | None = None,
    comments_repo: FakeCommentsRepository | None = None,
    likes_repo: FakeLikesRepository | None = None,
) -> FakeUnitOfWork:
    return FakeUnitOfWork(
        session=session,
        repositories={
            "posts": posts_repo or FakePostsRepository(),
            "comments": comments_repo or FakeCommentsRepository(),
            "likes": likes_repo or FakeLikesRepository(),
        },
    )


@pytest.mark.asyncio
async def test_create_comment_success(fake_session: FakeAsyncSession) -> None:
    user = build_user()
    post = build_post(author=user)
    comment = build_comment(author_id=user.id, post_id=post.id, content="Nice!")

    uow = build_uow(
        fake_session,
        FakePostsRepository(post=post),
        FakeCommentsRepository(comment=comment),
    )

    use_case = CreateCommentUseCase(uow=uow)
    data = CommentCreate(content="Nice!")

    result = await use_case.execute(user_id=user.id, post_id=post.id, data=data)

    assert result.content == "Nice!"
    uow.comments.create.assert_awaited_once()
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_comment_success(fake_session: FakeAsyncSession) -> None:
    user = build_user()
    comment = build_comment(author_id=user.id)

    uow = build_uow(fake_session, comments_repo=FakeCommentsRepository(comment=comment))

    use_case = DeleteCommentUseCase(uow=uow)
    await use_case.execute(
        user_id=user.id, post_id=comment.post_id, comment_id=comment.id
    )

    uow.comments.delete.assert_awaited_once()
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_toggle_like_creates_like(fake_session: FakeAsyncSession) -> None:
    user = build_user()
    author = build_user()
    post = build_post(author=author)

    uow = build_uow(
        fake_session,
        FakePostsRepository(post=post),
        likes_repo=FakeLikesRepository(like=None),  # No existing like
    )

    use_case = ToggleLikeUseCase(uow=uow)
    await use_case.execute(user_id=user.id, post_id=post.id, action="like")

    uow.likes.create.assert_awaited_once()
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_toggle_like_removes_like(fake_session: FakeAsyncSession) -> None:
    user = build_user()
    author = build_user()
    post = build_post(author=author)
    like = build_like(user_id=user.id, post_id=post.id)

    uow = build_uow(
        fake_session,
        FakePostsRepository(post=post),
        likes_repo=FakeLikesRepository(like=like),  # Existing like
    )

    use_case = ToggleLikeUseCase(uow=uow)
    await use_case.execute(user_id=user.id, post_id=post.id, action="unlike")

    uow.likes.delete.assert_awaited_once()
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_toggle_like_self_post_denied(fake_session: FakeAsyncSession) -> None:
    user = build_user()
    post = build_post(author=user)  # User is author

    uow = build_uow(fake_session, FakePostsRepository(post=post))

    use_case = ToggleLikeUseCase(uow=uow)

    with pytest.raises(
        PermissionDeniedException, match="You cannot like your own post."
    ):
        await use_case.execute(user_id=user.id, post_id=post.id, action="like")
