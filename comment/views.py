from datetime import date

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import HttpRequest
from ninja import Router, Query
from ninja.errors import HttpError
from ninja.pagination import (
    PageNumberPagination,
    paginate
)
from ninja.responses import Response
from ninja_extra import status
from ninja_jwt.authentication import JWTAuth

from integrations.gemini import block_decision
from integrations.tasks import auto_reply_to_comment
from comment.models import Comment
from comment.decorators import (
    comment_exist,
    has_delete_access,
    has_edit_access
)
import comment.schemas as schemas
from post.decorators import post_exist
from social_service.settings import (
    PAGE_PAGINATION_NUMBER,
    BREAKDOWN_PAGINATION_NUMBER
)

router = Router()


@router.get(
    "/post/{post_id}",
    response={200: list[schemas.CommentSchema], 404: str}
)
@paginate(PageNumberPagination, page_size=PAGE_PAGINATION_NUMBER)
@post_exist
def get_comments_by_post(
        request: HttpRequest, post_id: int
) -> list[schemas.CommentSchema]:
    comments = Comment.objects.filter(
        post_id=post_id
    ).select_related("author").prefetch_related("replies")
    if not comments.exists():
        raise HttpError(
            status.HTTP_404_NOT_FOUND,
            "Comments not found"
        )
    return schemas.CommentSchema.build_comment_hierarchy(comments)


@router.patch(
    "/{comment_id}",
    response={200: schemas.CommentSchema, 400: str, 404: str}, auth=JWTAuth()
)
@comment_exist
@has_edit_access
def edit_comment(
        request: HttpRequest, comment_id: int,
        payload: schemas.UpdateCommentSchema
) -> schemas.CommentSchema:
    comment = Comment.objects.get(id=comment_id)
    comment.text = payload.text
    comment.save()
    return schemas.CommentSchema.from_orm(comment)


@router.delete(
    "/{comment_id}",
    response={200: str, 403: str, 404: str}, auth=JWTAuth()
)
@comment_exist
@has_delete_access
def delete_comment(
        request: HttpRequest, comment_id: int
) -> Response:
    comment = Comment.objects.get(id=comment_id)
    comment.delete()
    return Response(
        {"detail": "Comment has been successfully deleted"},
        status=status.HTTP_200_OK
    )


@router.post(
    "/create/{post_id}",
    response={200: schemas.CommentSchema, 400: str},
    auth=JWTAuth()
)
@post_exist
def create_comment(
        request: HttpRequest, post_id: int,
        payload: schemas.CreateCommentSchema
) -> schemas.CommentSchema:
    decision = block_decision(payload.text)
    comment = Comment(
        post_id=post_id,
        author=request.user,
        text=payload.text,
        is_blocked=decision
    )
    if payload.parent_id:
        try:
            parent = Comment.objects.get(id=payload.parent_id)
            if parent.post_id != post_id:
                raise HttpError(
                    status.HTTP_400_BAD_REQUEST,
                    "Parent comment should be from the same post"
                )
            comment.parent = parent
        except Comment.DoesNotExist:
            raise HttpError(
                status.HTTP_400_BAD_REQUEST,
                "Parent comment does not exist"
            )
    comment.save()

    if (
            comment.post.reply_on_comments
            and comment.post.author != comment.author
    ):
        auto_reply_to_comment.apply_async(
            kwargs={"comment_id": comment.id},
            countdown=int(comment.post.reply_time.total_seconds())
        )

    return schemas.CommentSchema.from_orm(comment)


def get_comments_daily_breakdown(date_from: date, date_to: date) -> list[schemas.CommentAnalytics]:
    comments_aggregation = (
        Comment.objects
        .filter(created_at__date__range=(date_from, date_to))
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(
            created_comments=Count('id'),
            blocked_comments=Count('id', filter=Q(is_blocked=True))
        )
        .order_by('date')
    )

    analytics = [
        schemas.CommentAnalytics(
            date=item['date'],
            created_comments=item['created_comments'],
            blocked_comments=item['blocked_comments']
        )
        for item in comments_aggregation
    ]

    return analytics

@router.get(
    "/daily-breakdown/",
    response=list[schemas.CommentAnalytics]
)
@paginate(PageNumberPagination, page_size=BREAKDOWN_PAGINATION_NUMBER)
def comments_daily_breakdown(
        request: HttpRequest,
        params: schemas.DateRangeSchema = Query(...)
) -> list[schemas.CommentAnalytics]:
    date_from = params.date_from
    date_to = params.date_to

    if date_from > date_to:
        raise HttpError(
            status.HTTP_400_BAD_REQUEST,
            "Incorrect range was entered"
        )

    return get_comments_daily_breakdown(date_from, date_to)