from datetime import datetime, date
from typing import Optional

from ninja import (
    Schema,
    Field
)

from user.schemas import UserSchema


class CommentSchema(Schema):
    id: int
    author: UserSchema
    text: str = Field(min_length=6, max_length=255)
    created_at: datetime
    parent: Optional["CommentSchema"] = None
    is_blocked: bool


class CreateUpdateCommentSchema(Schema):
    text: str = Field(min_length=6, max_length=255)


class DateRangeSchema(Schema):
    date_from: date
    date_to: date

class CommentAnalytics(Schema):
    date: date
    created_comments: int
    blocked_comments: int
