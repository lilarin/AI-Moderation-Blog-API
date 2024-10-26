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
    reply_on_comments: bool = False
    reply_time: Optional[timedelta] = timedelta(minutes=5)
    is_blocked: bool
    comments: list[CommentSchema] = []

    @staticmethod
    def resolve_reply_time(obj):
        if not obj.reply_on_comments:
            return None
        return obj.reply_time


class CreatePostSchema(Schema):
    title: str = Field(min_length=6, max_length=255)
    text: str = Field(min_length=6, max_length=255)
    reply_on_comments: Optional[bool] = False
    reply_time: Optional[timedelta] = None


class UpdatePostSchema(Schema):
    title: Optional[str] = Field(None, min_length=6, max_length=255)
    text: Optional[str] = Field(None, min_length=6, max_length=255)
    reply_time: Optional[timedelta] = None
