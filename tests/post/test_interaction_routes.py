from unittest.mock import AsyncMock

from httpx import AsyncClient
import pytest

from src.core.schemas import SuccessResponse
from src.post.dependencies import get_comment_service
from src.post.schemas import CommentViewModel
from src.post.usecases.interaction_usecases import (
    get_create_comment_use_case,
    get_delete_comment_use_case,
    get_toggle_like_use_case,
)
from src.user.auth.dependencies import get_current_user
from tests.factories.post_factory import build_comment, build_post
from tests.factories.user_factory import build_user
from tests.helpers.overrides import DependencyOverrides
from tests.helpers.providers import ProvideValue


class FakeCreateCommentUseCase:
    def __init__(self, result: CommentViewModel) -> None:
        self.execute = AsyncMock(return_value=result)


class FakeDeleteCommentUseCase:
    def __init__(self, result: SuccessResponse) -> None:
        self.execute = AsyncMock(return_value=result)


class FakeToggleLikeUseCase:
    def __init__(self, result: SuccessResponse) -> None:
        self.execute = AsyncMock(return_value=result)


class FakeCommentService:
    def __init__(self, list_result: tuple[list[CommentViewModel], int]) -> None:
        self.get_paginated_list = AsyncMock(return_value=list_result)


@pytest.mark.asyncio
async def test_create_comment_route(
    async_client_with_fakes: AsyncClient,
    dependency_overrides: DependencyOverrides,
) -> None:
    user = build_user()
    post = build_post(author=user)
    comment = build_comment(author_id=user.id, post_id=post.id, content="My Comment!")

    dependency_overrides.set(get_current_user, ProvideValue(user))
    dependency_overrides.set(
        get_create_comment_use_case,
        ProvideValue(
            FakeCreateCommentUseCase(CommentViewModel.model_validate(comment))
        ),
    )

    response = await async_client_with_fakes.post(
        f"/v1/posts/{post.id}/comments",
        json={"content": "My Comment!"},
    )

    assert response.status_code == 201
    assert response.json()["content"] == "My Comment!"


@pytest.mark.asyncio
async def test_list_comments_route(
    async_client_with_fakes: AsyncClient,
    dependency_overrides: DependencyOverrides,
) -> None:
    user = build_user()
    post = build_post(author=user)
    comment1 = build_comment(author_id=user.id, post_id=post.id, content="C1")
    comment2 = build_comment(author_id=user.id, post_id=post.id, content="C2")

    dependency_overrides.set(
        get_comment_service,
        ProvideValue(FakeCommentService(list_result=([comment1, comment2], 2))),
    )

    response = await async_client_with_fakes.get(
        f"/v1/posts/{post.id}/comments?page=1&size=10"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_delete_comment_route(
    async_client_with_fakes: AsyncClient,
    dependency_overrides: DependencyOverrides,
) -> None:
    user = build_user()
    post = build_post(author=user)
    comment = build_comment(author_id=user.id, post_id=post.id)

    dependency_overrides.set(get_current_user, ProvideValue(user))
    dependency_overrides.set(
        get_delete_comment_use_case,
        ProvideValue(FakeDeleteCommentUseCase(SuccessResponse(success=True))),
    )

    response = await async_client_with_fakes.delete(
        f"/v1/posts/{post.id}/comments/{comment.id}"
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_toggle_like_route(
    async_client_with_fakes: AsyncClient,
    dependency_overrides: DependencyOverrides,
) -> None:
    user = build_user()
    post = build_post(author=user)

    dependency_overrides.set(get_current_user, ProvideValue(user))
    dependency_overrides.set(
        get_toggle_like_use_case,
        ProvideValue(FakeToggleLikeUseCase(SuccessResponse(success=True))),
    )

    response = await async_client_with_fakes.post(f"/v1/posts/{post.id}/like")
    assert response.status_code == 200

    response2 = await async_client_with_fakes.delete(f"/v1/posts/{post.id}/like")
    assert response2.status_code == 200
