from uuid import UUID

from fastapi import Depends

from src.core.database.session import get_unit_of_work
from src.core.database.uow import ApplicationUnitOfWork, RepositoryProtocol
from src.core.errors.exceptions import (
    InstanceNotFoundException,
    PermissionDeniedException,
)
from src.post.schemas import PostCreate, PostUpdate, PostViewModel


class CreatePostUseCase:
    def __init__(self, uow: ApplicationUnitOfWork[RepositoryProtocol]) -> None:
        self.uow = uow

    async def execute(self, user_id: UUID, data: PostCreate) -> PostViewModel:
        async with self.uow as uow:
            post = await uow.posts.create(
                uow.session, {"author_id": user_id, **data.model_dump()}
            )
            await uow.commit()
            return PostViewModel.model_validate(post)


class UpdatePostUseCase:
    def __init__(self, uow: ApplicationUnitOfWork[RepositoryProtocol]) -> None:
        self.uow = uow

    async def execute(
        self, user_id: UUID, post_id: UUID, data: PostUpdate
    ) -> PostViewModel:
        async with self.uow as uow:
            post = await uow.posts.get_single(uow.session, id=post_id)
            if not post:
                raise InstanceNotFoundException("Post not found.")

            if post.author_id != user_id:
                raise PermissionDeniedException("You can only edit your own posts.")

            updated_data = data.model_dump(exclude_unset=True)
            if updated_data:
                post = await uow.posts.update(uow.session, updated_data, id=post_id)

            await uow.commit()
            return PostViewModel.model_validate(post)


class DeletePostUseCase:
    def __init__(self, uow: ApplicationUnitOfWork[RepositoryProtocol]) -> None:
        self.uow = uow

    async def execute(self, user_id: UUID, post_id: UUID) -> None:
        async with self.uow as uow:
            post = await uow.posts.get_single(uow.session, id=post_id)
            if not post:
                raise InstanceNotFoundException("Post not found.")

            if post.author_id != user_id:
                raise PermissionDeniedException("You can only delete your own posts.")

            await uow.posts.delete(uow.session, id=post_id)
            await uow.commit()


def get_create_post_use_case(
    uow: ApplicationUnitOfWork[RepositoryProtocol] = Depends(get_unit_of_work),
) -> CreatePostUseCase:
    return CreatePostUseCase(uow=uow)


def get_update_post_use_case(
    uow: ApplicationUnitOfWork[RepositoryProtocol] = Depends(get_unit_of_work),
) -> UpdatePostUseCase:
    return UpdatePostUseCase(uow=uow)


def get_delete_post_use_case(
    uow: ApplicationUnitOfWork[RepositoryProtocol] = Depends(get_unit_of_work),
) -> DeletePostUseCase:
    return DeletePostUseCase(uow=uow)
