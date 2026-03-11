from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.session import get_session
from src.core.errors.exceptions import InstanceNotFoundException
from src.core.pagination.schemas import (
    PaginatedResponse,
    PaginationParams,
    make_paginated_response,
)
from src.core.schemas import SuccessResponse
from src.post.dependencies import get_comment_service, get_post_service
from src.post.schemas import (
    CommentCreate,
    CommentViewModel,
    PostCreate,
    PostUpdate,
    PostViewModel,
    PostWithDetailsViewModel,
)
from src.post.services import CommentService, PostService
from src.post.usecases.interaction_usecases import (
    CreateCommentUseCase,
    DeleteCommentUseCase,
    ToggleLikeUseCase,
    get_create_comment_use_case,
    get_delete_comment_use_case,
    get_toggle_like_use_case,
)
from src.post.usecases.post_usecases import (
    CreatePostUseCase,
    DeletePostUseCase,
    UpdatePostUseCase,
    get_create_post_use_case,
    get_delete_post_use_case,
    get_update_post_use_case,
)
from src.user.auth.dependencies import get_current_user, get_optional_current_user
from src.user.auth.permissions.checker import require_permission
from src.user.auth.permissions.enum import Permission
from src.user.models import User

router = APIRouter()


# -----------------------------------------------------------------------------
# Posts
# -----------------------------------------------------------------------------


@router.get("", response_model=PaginatedResponse[PostViewModel])
async def list_posts(
    pagination: Annotated[PaginationParams, Depends()],
    post_service: Annotated[PostService, Depends(get_post_service)],
    session: AsyncSession = Depends(get_session),
) -> PaginatedResponse[PostViewModel]:
    """Get a paginated list of all posts."""
    result = await post_service.get_paginated_list(session, pagination=pagination)
    if isinstance(result, tuple):
        items, total = result
        return make_paginated_response(
            items=items, total=total, pagination=pagination, schema=PostViewModel
        )
    return result


@router.post("", response_model=PostViewModel, status_code=201)
async def create_post(
    data: PostCreate,
    current_user: Annotated[User, Depends(require_permission(Permission.CREATE_POSTS))],
    use_case: Annotated[CreatePostUseCase, Depends(get_create_post_use_case)],
) -> PostViewModel:
    """Create a new post."""
    return await use_case.execute(user_id=current_user.id, data=data)


@router.get("/{post_id}", response_model=PostWithDetailsViewModel)
async def get_post(
    post_id: UUID,
    post_service: Annotated[PostService, Depends(get_post_service)],
    session: AsyncSession = Depends(get_session),
    current_user: User | None = Depends(get_optional_current_user),
) -> PostWithDetailsViewModel:
    """Get a single post with extended details (author, comments, likes)."""
    post = await post_service.get_single(session, id=post_id)
    if not post:
        raise InstanceNotFoundException("Post not found")
    return PostWithDetailsViewModel.model_validate(post)


@router.patch("/{post_id}", response_model=PostViewModel)
async def update_post(
    post_id: UUID,
    data: PostUpdate,
    current_user: Annotated[User, Depends(require_permission(Permission.CREATE_POSTS))],
    use_case: Annotated[UpdatePostUseCase, Depends(get_update_post_use_case)],
) -> PostViewModel:
    """Update a post. User must be the author."""
    return await use_case.execute(user_id=current_user.id, post_id=post_id, data=data)


@router.delete("/{post_id}", response_model=SuccessResponse)
async def delete_post(
    post_id: UUID,
    current_user: Annotated[User, Depends(require_permission(Permission.CREATE_POSTS))],
    use_case: Annotated[DeletePostUseCase, Depends(get_delete_post_use_case)],
) -> SuccessResponse:
    """Delete a post. User must be the author."""
    await use_case.execute(user_id=current_user.id, post_id=post_id)
    return SuccessResponse(success=True)


# -----------------------------------------------------------------------------
# Comments
# -----------------------------------------------------------------------------


@router.get("/{post_id}/comments", response_model=PaginatedResponse[CommentViewModel])
async def list_comments(
    post_id: UUID,
    pagination: Annotated[PaginationParams, Depends()],
    comment_service: Annotated[CommentService, Depends(get_comment_service)],
    session: AsyncSession = Depends(get_session),
    current_user: User | None = Depends(get_optional_current_user),
) -> PaginatedResponse[CommentViewModel]:
    """Get comments for a specific post."""
    result = await comment_service.get_paginated_list(
        session, pagination=pagination, post_id=post_id
    )
    if isinstance(result, tuple):
        items, total = result
        return make_paginated_response(
            items=items, total=total, pagination=pagination, schema=CommentViewModel
        )
    return result


@router.post("/{post_id}/comments", response_model=CommentViewModel, status_code=201)
async def create_comment(
    post_id: UUID,
    data: CommentCreate,
    current_user: Annotated[User, Depends(require_permission(Permission.CREATE_POSTS))],
    use_case: Annotated[CreateCommentUseCase, Depends(get_create_comment_use_case)],
) -> CommentViewModel:
    """Add a comment to a post."""
    return await use_case.execute(user_id=current_user.id, post_id=post_id, data=data)


@router.delete("/{post_id}/comments/{comment_id}", response_model=SuccessResponse)
async def delete_comment(
    post_id: UUID,
    comment_id: UUID,
    current_user: Annotated[User, Depends(require_permission(Permission.CREATE_POSTS))],
    use_case: Annotated[DeleteCommentUseCase, Depends(get_delete_comment_use_case)],
) -> SuccessResponse:
    """Delete a comment. User must be the author."""
    await use_case.execute(
        user_id=current_user.id, post_id=post_id, comment_id=comment_id
    )
    return SuccessResponse(success=True)


# -----------------------------------------------------------------------------
# Likes
# -----------------------------------------------------------------------------


@router.post("/{post_id}/like", response_model=SuccessResponse)
async def like_post(
    post_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ToggleLikeUseCase, Depends(get_toggle_like_use_case)],
) -> SuccessResponse:
    """Like a post."""
    await use_case.execute(user_id=current_user.id, post_id=post_id, action="like")
    return SuccessResponse(success=True)


@router.delete("/{post_id}/like", response_model=SuccessResponse)
async def unlike_post(
    post_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    use_case: Annotated[ToggleLikeUseCase, Depends(get_toggle_like_use_case)],
) -> SuccessResponse:
    """Unlike a post."""
    await use_case.execute(user_id=current_user.id, post_id=post_id, action="unlike")
    return SuccessResponse(success=True)
