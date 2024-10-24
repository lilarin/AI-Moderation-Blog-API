from datetime import (
    date,
    timedelta
)

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

from comment.models import Comment
from comment.decorators import (
    comment_exist,
    has_delete_access,
    has_edit_access
)
from comment.schemas import (
    CommentSchema,
    CreateUpdateCommentSchema,
    DateRangeSchema,
    CommentAnalytics
)
from post.decorators import post_exist
from social_service.settings import (
    PAGE_PAGINATION_NUMBER,
    BREAKDOWN_PAGINATION_NUMBER
)

router = Router()


@router.patch(
    "/{comment_id}",
    response={200: CommentSchema, 400: str, 404: str}, auth=JWTAuth()
)
@comment_exist
@has_edit_access
def edit_comment(
        request: HttpRequest, comment_id: int,
        payload: CreateUpdateCommentSchema
) -> CommentSchema:
    comment = Comment.objects.get(id=comment_id)
    comment.text = payload.text
    comment.save()
    return CommentSchema.from_orm(comment)


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


@router.get(
    "/{post_id}",
    response={200: list[CommentSchema], 404: str}
)
@paginate(PageNumberPagination, page_size=PAGE_PAGINATION_NUMBER)
@post_exist
def get_comments_by_post(
        request: HttpRequest, post_id: int
) -> list[CommentSchema]:
    comments = Comment.objects.filter(
        post_id=post_id
    )

    if not comments.exists():
        raise HttpError(
            status.HTTP_404_NOT_FOUND,
            "Comments not found")

    return [CommentSchema.from_orm(comment) for comment in comments]


@router.post(
    "/create/{post_id}",
    response={200: CommentSchema, 400: str},
    auth=JWTAuth()
)
@post_exist
def create_comment(
        request: HttpRequest, post_id: int,
        payload: CreateUpdateCommentSchema
) -> CommentSchema:
    comment = Comment(
        post_id=post_id,
        author=request.user,
        text=payload.text
    )
    comment.save()
    return CommentSchema.from_orm(comment)


def get_comments_count(target_date: date) -> tuple[int, int]:
    total_comments = Comment.objects.filter(
        created_at__date=target_date
    ).count()
    blocked_comments = Comment.objects.filter(
        created_at__date=target_date, is_blocked=True
    ).count()
    return total_comments, blocked_comments


@router.get(
    "/comments-daily-breakdown/",
    response=list[CommentAnalytics]
)
@paginate(PageNumberPagination, page_size=BREAKDOWN_PAGINATION_NUMBER)
def comments_daily_breakdown(
        request: HttpRequest,
        params: DateRangeSchema = Query(...)
) -> list[CommentAnalytics]:
    date_from = params.date_from
    date_to = params.date_to

    if date_from > date_to:
        raise HttpError(
            status.HTTP_400_BAD_REQUEST,
            "Incorrect range was entered"
        )

    analytics = []
    for i in range((date_to - date_from).days + 1):
        search_date = date_from + timedelta(days=i)
        created_comments, blocked_comments = get_comments_count(search_date)
        analytics.append(
            CommentAnalytics(
                date=search_date,
                created_comments=created_comments,
                blocked_comments=blocked_comments
            )
        )
    return analytics