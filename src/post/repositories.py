from src.core.database.repositories import BaseRepository
from src.post.models import Comment, Like, Post


class PostRepository(BaseRepository[Post]):
    model = Post


class CommentRepository(BaseRepository[Comment]):
    model = Comment


class LikeRepository(BaseRepository[Like]):
    model = Like
