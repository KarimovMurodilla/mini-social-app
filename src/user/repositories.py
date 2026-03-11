from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from loggers import get_logger
from src.core.database.repositories import SoftDeleteRepository
from src.post.models import Post
from src.user.models import User

logger = get_logger(__name__)


class UserRepository(SoftDeleteRepository[User]):
    model = User

    async def get_feed_users_paginated(
        self, session: AsyncSession, *, page: int, size: int
    ) -> tuple[list[User], int]:
        stmt = select(User).where(User.is_deleted == False)  # noqa: E712

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count: int = await session.scalar(count_stmt) or 0

        stmt = stmt.options(selectinload(User.posts).selectinload(Post.likes))
        stmt = stmt.offset((page - 1) * size).limit(size)

        result = await session.execute(stmt)
        users = list(result.scalars().all())

        return users, total_count
