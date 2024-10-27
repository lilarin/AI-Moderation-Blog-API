from datetime import (
    datetime,
    date
)
from typing import Optional
from django.db.models import QuerySet
from ninja import (
    Schema,
    Field
)
from comment.models import Comment
from user.schemas import UserSchema


class BaseCommentSchema(Schema):
    text: str = Field(min_length=6, max_length=255)


class CommentSchema(BaseCommentSchema):
    id: int
    author: UserSchema
    created_at: datetime
    is_blocked: bool
    replies: list["CommentSchema"] = []

    @staticmethod
    def build_comment_hierarchy(
            comments: QuerySet[Comment]
    ) -> list["CommentSchema"]:
        comment_map = {
            comment.id: CommentSchema.from_orm(comment)
            for comment in comments
        }
        root_comments = []

        for comment in comments:
            if comment.parent is None:
                root_comments.append(comment_map[comment.id])
            else:
                parent_comment = comment_map[comment.parent.id]
                if comment_map[comment.id] not in parent_comment.replies:
                    parent_comment.replies.append(comment_map[comment.id])

        return root_comments


class CreateCommentSchema(BaseCommentSchema):
    parent_id: Optional[int] = None


class UpdateCommentSchema(BaseCommentSchema):
    pass


class DateRangeSchema(Schema):
    date_from: date
    date_to: date


class CommentAnalytics(Schema):
    date: date
    created_comments: int
    blocked_comments: int
