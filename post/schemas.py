from datetime import (
    datetime,
    timedelta
)

from ninja import Schema

from comment.schemas import CommentSchema
from user.schemas import UserSchema


class PostSchema(Schema):
    id: int
    title: str
    text: str
    author: UserSchema
    created_at: datetime
    reply_time: timedelta
    is_blocked: bool
    comments: list[CommentSchema] = None


class CreatePostSchema(Schema):
    title: str
    text: str
    reply_time: timedelta
