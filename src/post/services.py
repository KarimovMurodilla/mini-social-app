from src.core.schemas import Base
from src.core.services import BaseService
from src.post.models import Comment, Like, Post
from src.post.repositories import CommentRepository, LikeRepository, PostRepository
from src.post.schemas import (
    CommentCreate,
    CommentViewModel,
    LikeViewModel,
    PostCreate,
    PostViewModel,
)


class PostService(BaseService[Post, PostCreate, Base, PostRepository, PostViewModel]):
    def __init__(self, repository: PostRepository):
        super().__init__(repository, response_schema=PostViewModel)


class CommentService(
    BaseService[Comment, CommentCreate, Base, CommentRepository, CommentViewModel]
):
    def __init__(self, repository: CommentRepository):
        super().__init__(repository, response_schema=CommentViewModel)


class LikeService(BaseService[Like, Base, Base, LikeRepository, LikeViewModel]):
    def __init__(self, repository: LikeRepository):
        super().__init__(repository, response_schema=LikeViewModel)
