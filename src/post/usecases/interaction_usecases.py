from uuid import UUID

from fastapi import Depends

from src.core.database.session import get_unit_of_work
from src.core.database.uow import ApplicationUnitOfWork, RepositoryProtocol
from src.core.errors.exceptions import (
    InstanceNotFoundException,
    PermissionDeniedException,
)
from src.post.schemas import CommentCreate, CommentViewModel


class CreateCommentUseCase:
    def __init__(self, uow: ApplicationUnitOfWork[RepositoryProtocol]) -> None:
        self.uow = uow

    async def execute(
        self, user_id: UUID, post_id: UUID, data: CommentCreate
    ) -> CommentViewModel:
        async with self.uow as uow:
            post = await uow.posts.get_single(uow.session, id=post_id)
            if not post:
                raise InstanceNotFoundException("Post not found.")

            comment = await uow.comments.create(
                uow.session,
                {
                    "author_id": user_id,
                    "post_id": post_id,
                    "content": data.content,
                },
            )
            await uow.commit()
            return CommentViewModel.model_validate(comment)


class DeleteCommentUseCase:
    def __init__(self, uow: ApplicationUnitOfWork[RepositoryProtocol]) -> None:
        self.uow = uow

    async def execute(self, user_id: UUID, post_id: UUID, comment_id: UUID) -> None:
        async with self.uow as uow:
            comment = await uow.comments.get_single(
                uow.session, id=comment_id, post_id=post_id
            )
            if not comment:
                raise InstanceNotFoundException("Comment not found.")

            if comment.author_id != user_id:
                raise PermissionDeniedException(
                    "You can only delete your own comments."
                )

            await uow.comments.delete(uow.session, id=comment_id)
            await uow.commit()


class ToggleLikeUseCase:
    def __init__(self, uow: ApplicationUnitOfWork[RepositoryProtocol]) -> None:
        self.uow = uow

    async def execute(self, user_id: UUID, post_id: UUID, action: str) -> None:
        """action is 'like' or 'unlike'"""
        async with self.uow as uow:
            post = await uow.posts.get_single(uow.session, id=post_id)
            if not post:
                raise InstanceNotFoundException("Post not found.")

            if post.author_id == user_id:
                raise PermissionDeniedException("You cannot like your own post.")

            like = await uow.likes.get_single(
                uow.session, user_id=user_id, post_id=post_id
            )

            if action == "like":
                if like:
                    raise PermissionDeniedException("You already liked this post.")
                await uow.likes.create(
                    uow.session, {"user_id": user_id, "post_id": post_id}
                )
            elif action == "unlike":
                if not like:
                    raise InstanceNotFoundException("You haven't liked this post yet.")
                await uow.likes.delete(uow.session, user_id=user_id, post_id=post_id)

            await uow.commit()


def get_create_comment_use_case(
    uow: ApplicationUnitOfWork[RepositoryProtocol] = Depends(get_unit_of_work),
) -> CreateCommentUseCase:
    return CreateCommentUseCase(uow=uow)


def get_delete_comment_use_case(
    uow: ApplicationUnitOfWork[RepositoryProtocol] = Depends(get_unit_of_work),
) -> DeleteCommentUseCase:
    return DeleteCommentUseCase(uow=uow)


def get_toggle_like_use_case(
    uow: ApplicationUnitOfWork[RepositoryProtocol] = Depends(get_unit_of_work),
) -> ToggleLikeUseCase:
    return ToggleLikeUseCase(uow=uow)
