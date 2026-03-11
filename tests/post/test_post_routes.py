from unittest.mock import AsyncMock

from httpx import AsyncClient
import pytest

from src.core.schemas import SuccessResponse
from src.post.dependencies import get_post_service
from src.post.schemas import PostViewModel, PostWithDetailsViewModel
from src.post.usecases.post_usecases import (
    get_create_post_use_case,
    get_delete_post_use_case,
)
from src.user.auth.dependencies import get_current_user
from tests.factories.post_factory import build_post
from tests.factories.user_factory import build_user
from tests.helpers.overrides import DependencyOverrides
from tests.helpers.providers import ProvideValue


class FakeCreatePostUseCase:
    def __init__(self, result: PostViewModel) -> None:
        self.execute = AsyncMock(return_value=result)


class FakeUpdatePostUseCase:
    def __init__(self, result: PostViewModel) -> None:
        self.execute = AsyncMock(return_value=result)


class FakeDeletePostUseCase:
    def __init__(self, result: SuccessResponse) -> None:
        self.execute = AsyncMock(return_value=result)


class FakePostService:
    def __init__(
        self,
        list_result: tuple[list[PostViewModel], int],
        single_result: PostWithDetailsViewModel | None,
    ) -> None:
        self.get_paginated_list = AsyncMock(return_value=list_result)
        self.get_single = AsyncMock(return_value=single_result)


@pytest.mark.asyncio
async def test_create_post_route(
    async_client_with_fakes: AsyncClient,
    dependency_overrides: DependencyOverrides,
) -> None:
    user = build_user()
    post = build_post(author=user, title="Test Title", content="C")

    dependency_overrides.set(get_current_user, ProvideValue(user))
    dependency_overrides.set(
        get_create_post_use_case,
        ProvideValue(FakeCreatePostUseCase(PostViewModel.model_validate(post))),
    )

    response = await async_client_with_fakes.post(
        "/v1/posts",
        json={"title": "Test Title", "content": "C"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Test Title"


@pytest.mark.asyncio
async def test_list_posts_route(
    async_client_with_fakes: AsyncClient,
    dependency_overrides: DependencyOverrides,
) -> None:
    user = build_user()
    post1 = build_post(author=user, title="P1")
    post2 = build_post(author=user, title="P2")

    dependency_overrides.set(
        get_post_service,
        ProvideValue(
            FakePostService(list_result=([post1, post2], 2), single_result=None)
        ),
    )

    response = await async_client_with_fakes.get("/v1/posts?page=1&size=10")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_single_post_route(
    async_client_with_fakes: AsyncClient,
    dependency_overrides: DependencyOverrides,
) -> None:
    user = build_user()
    post = build_post(author=user, title="P1")

    dependency_overrides.set(
        get_post_service,
        ProvideValue(FakePostService(list_result=([], 0), single_result=post)),
    )

    response = await async_client_with_fakes.get(f"/v1/posts/{post.id}")

    assert response.status_code == 200
    assert response.json()["title"] == "P1"


@pytest.mark.asyncio
async def test_delete_post_route(
    async_client_with_fakes: AsyncClient,
    dependency_overrides: DependencyOverrides,
) -> None:
    user = build_user()
    post = build_post(author=user)

    dependency_overrides.set(get_current_user, ProvideValue(user))
    dependency_overrides.set(
        get_delete_post_use_case,
        ProvideValue(FakeDeletePostUseCase(SuccessResponse(success=True))),
    )

    response = await async_client_with_fakes.delete(f"/v1/posts/{post.id}")

    assert response.status_code == 200
    assert response.json()["success"] is True
