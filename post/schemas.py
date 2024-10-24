from datetime import (
    datetime,
    timedelta
)
from typing import Optional

from ninja import (
    Schema,
    Field
)

from comment.schemas import CommentSchema
from user.schemas import UserSchema


class PostSchema(Schema):
    id: int
    title: str = Field(min_length=6, max_length=255)
    text: str = Field(min_length=6, max_length=255)
    author: UserSchema
    created_at: datetime
    reply_time: timedelta
    is_blocked: bool
    comments: list[CommentSchema] = None


class CreatePostSchema(Schema):
    title: str = Field(min_length=6, max_length=255)
    text: str = Field(min_length=6, max_length=255)
    reply_time: timedelta


class UpdatePostSchema(Schema):
    title: Optional[str] = Field(None, min_length=6, max_length=255)
    text: Optional[str] = Field(None, min_length=6, max_length=255)
    reply_time: Optional[timedelta] = None
