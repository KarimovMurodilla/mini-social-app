from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.core.errors.exceptions import (
    InstanceNotFoundException,
    PermissionDeniedException,
)
from src.post.models import Post
from src.post.schemas import PostCreate, PostUpdate
from src.post.usecases.post_usecases import (
    CreatePostUseCase,
    DeletePostUseCase,
    UpdatePostUseCase,
)
from tests.factories.post_factory import build_post
from tests.factories.user_factory import build_user
from tests.fakes.db import FakeAsyncSession, FakeUnitOfWork


class FakePostsRepository:
    def __init__(
        self,
        post: Post | None = None,
        updated_post: Post | None = None,
    ) -> None:
        self._post = post
        self._updated_post = updated_post or post
        self.create = AsyncMock(side_effect=self._create)
        self.get_single = AsyncMock(side_effect=self._get_single)
        self.update = AsyncMock(side_effect=self._update)
        self.delete = AsyncMock(side_effect=self._delete)

    async def _create(self, session: FakeAsyncSession, data: dict) -> Post:
        if self._post:
            return self._post
        return build_post(
            author_id=data["author_id"], title=data["title"], content=data["content"]
        )

    async def _get_single(
        self, session: FakeAsyncSession, **filters: object
    ) -> Post | None:
        return self._post

    async def _update(
        self, session: FakeAsyncSession, data: dict, **filters: object
    ) -> Post | None:
        return self._updated_post

    async def _delete(self, session: FakeAsyncSession, **filters: object) -> None:
        pass


def build_uow(
    session: FakeAsyncSession,
    posts_repo: FakePostsRepository,
) -> FakeUnitOfWork:
    return FakeUnitOfWork(session=session, repositories={"posts": posts_repo})


@pytest.mark.asyncio
async def test_create_post_success(fake_session: FakeAsyncSession) -> None:
    user = build_user()
    posts_repo = FakePostsRepository()
    uow = build_uow(fake_session, posts_repo)

    use_case = CreatePostUseCase(uow=uow)
    data = PostCreate(title="My title", content="My content")

    result = await use_case.execute(user_id=user.id, data=data)

    assert result.title == "My title"
    assert result.content == "My content"
    posts_repo.create.assert_awaited_once()
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_post_success(fake_session: FakeAsyncSession) -> None:
    user = build_user()
    post = build_post(author=user, title="Old Title")
    updated_post = build_post(author=user, title="New Title", post_id=post.id)

    posts_repo = FakePostsRepository(post=post, updated_post=updated_post)
    uow = build_uow(fake_session, posts_repo)

    use_case = UpdatePostUseCase(uow=uow)
    data = PostUpdate(title="New Title")

    result = await use_case.execute(user_id=user.id, post_id=post.id, data=data)

    assert result.title == "New Title"
    posts_repo.update.assert_awaited_once()
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_post_not_found(fake_session: FakeAsyncSession) -> None:
    posts_repo = FakePostsRepository(post=None)
    uow = build_uow(fake_session, posts_repo)

    use_case = UpdatePostUseCase(uow=uow)
    data = PostUpdate(title="New Title")

    with pytest.raises(InstanceNotFoundException, match="Post not found."):
        await use_case.execute(user_id=uuid4(), post_id=uuid4(), data=data)


@pytest.mark.asyncio
async def test_update_post_permission_denied(fake_session: FakeAsyncSession) -> None:
    other_user = build_user()
    post = build_post(author=other_user)

    posts_repo = FakePostsRepository(post=post)
    uow = build_uow(fake_session, posts_repo)

    use_case = UpdatePostUseCase(uow=uow)
    data = PostUpdate(title="New Title")

    with pytest.raises(
        PermissionDeniedException, match="You can only edit your own posts."
    ):
        await use_case.execute(user_id=uuid4(), post_id=post.id, data=data)


@pytest.mark.asyncio
async def test_delete_post_success(fake_session: FakeAsyncSession) -> None:
    user = build_user()
    post = build_post(author=user)

    posts_repo = FakePostsRepository(post=post)
    uow = build_uow(fake_session, posts_repo)

    use_case = DeletePostUseCase(uow=uow)

    await use_case.execute(user_id=user.id, post_id=post.id)

    posts_repo.delete.assert_awaited_once()
    uow.commit.assert_awaited_once()
