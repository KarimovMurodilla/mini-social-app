from fastapi import Depends

from src.post.repositories import CommentRepository, LikeRepository, PostRepository
from src.post.services import CommentService, LikeService, PostService


# Repositories
def get_post_repository() -> PostRepository:
    return PostRepository()


def get_comment_repository() -> CommentRepository:
    return CommentRepository()


def get_like_repository() -> LikeRepository:
    return LikeRepository()


# Services
def get_post_service(
    repository: PostRepository = Depends(get_post_repository),
) -> PostService:
    return PostService(repository=repository)


def get_comment_service(
    repository: CommentRepository = Depends(get_comment_repository),
) -> CommentService:
    return CommentService(repository=repository)


def get_like_service(
    repository: LikeRepository = Depends(get_like_repository),
) -> LikeService:
    return LikeService(repository=repository)
