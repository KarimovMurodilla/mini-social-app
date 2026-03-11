from datetime import datetime

from fastapi import Depends

from src.core.database.session import get_unit_of_work
from src.core.database.uow.abstract import RepositoryProtocol
from src.core.database.uow.application import ApplicationUnitOfWork
from src.core.pagination.schemas import PaginationParams
from src.post.schemas import FeedPostViewModel, FeedViewModel


class GetFeedUseCase:
    def __init__(self, uow: ApplicationUnitOfWork[RepositoryProtocol]) -> None:
        self.uow = uow

    async def execute(
        self,
        pagination: PaginationParams,
        search: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> tuple[list[FeedViewModel], int]:
        async with self.uow as uow:
            users, total_count = await uow.users.get_feed_users_paginated(
                uow.session, page=pagination.page, size=pagination.size
            )

        # 4. Filter posts based on logic in Python memory
        feed_items = []
        date_from_dt = datetime.fromisoformat(date_from) if date_from else None
        date_to_dt = datetime.fromisoformat(date_to) if date_to else None

        for user in users:
            filtered_posts = []
            for post in user.posts:
                # apply filters
                if search:
                    s = search.lower()
                    if s not in post.title.lower() and s not in post.content.lower():
                        continue

                if date_from_dt and post.created_at < date_from_dt:
                    continue

                if date_to_dt and post.created_at > date_to_dt:
                    continue

                # Add to filtered posts
                post_view = FeedPostViewModel(
                    id=post.id,
                    title=post.title,
                    content=post.content,
                    likes=[like.user_id for like in post.likes],  # Just the uuids
                )
                filtered_posts.append(post_view)

            feed_view = FeedViewModel(username=user.username, posts=filtered_posts)
            feed_items.append(feed_view)

        return feed_items, total_count


def get_feed_use_case(
    uow: ApplicationUnitOfWork[RepositoryProtocol] = Depends(get_unit_of_work),
) -> GetFeedUseCase:
    return GetFeedUseCase(uow=uow)
