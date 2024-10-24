from datetime import datetime

from ninja import Schema

from user.schemas import UserSchema


class CommentSchema(Schema):
    author: UserSchema
    text: str
    created_at: datetime
    is_blocked: bool