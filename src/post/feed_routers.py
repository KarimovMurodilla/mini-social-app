from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.core.pagination.schemas import (
    PaginatedResponse,
    PaginationParams,
    make_paginated_response,
)
from src.post.schemas import FeedViewModel
from src.post.usecases.feed_usecases import GetFeedUseCase, get_feed_use_case

router = APIRouter()


@router.get("", response_model=PaginatedResponse[FeedViewModel])
async def get_feed(
    pagination: Annotated[PaginationParams, Depends()],
    use_case: Annotated[GetFeedUseCase, Depends(get_feed_use_case)],
    search: str | None = Query(None, description="Search by title or content"),
    date_from: str | None = Query(None, description="Filter from date (ISO format)"),
    date_to: str | None = Query(None, description="Filter to date (ISO format)"),
) -> PaginatedResponse[FeedViewModel]:
    """Get the feed: a list of users with their posts and likes."""
    items, total_count = await use_case.execute(
        pagination=pagination,
        search=search,
        date_from=date_from,
        date_to=date_to,
    )

    return make_paginated_response(
        items=items, total=total_count, pagination=pagination, schema=FeedViewModel
    )
