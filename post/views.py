from django.http import HttpRequest
from ninja import Router
from ninja.responses import Response
from ninja.pagination import (
    paginate,
    PageNumberPagination
)
from ninja_extra import status
from ninja_jwt.authentication import JWTAuth

from integrations.gemini import block_decision
from social_service.settings import PAGE_PAGINATION_NUMBER
from post.decorators import (
    post_exist,
    has_delete_access,
    has_edit_access
)
from post.models import Post
import post.schemas as schemas

router = Router()


@router.get("", response=list[schemas.PostSchema])
@paginate(PageNumberPagination, page_size=PAGE_PAGINATION_NUMBER)
def get_posts(request: HttpRequest) -> list[schemas.PostSchema]:
    posts = Post.objects.prefetch_related(
        "comments__replies", "author"
    )
    post_schemas = []

    for post in posts:
        post_schema = schemas.PostSchema.from_orm(post)
        post_schema.comments = schemas.CommentSchema.build_comment_hierarchy(
            post.comments.all()
        )
        post_schemas.append(post_schema)

    return post_schemas


@router.post(
    "",
    response={200: schemas.PostSchema, 400: str},
    auth=JWTAuth()
)
def create_post(
        request: HttpRequest, payload: schemas.CreatePostSchema
) -> schemas.PostSchema:
    decision = block_decision(payload.title + payload.text)
    post = Post(
        author=request.user,
        title=payload.title,
        text=payload.text,
        is_blocked=decision
    )
    if payload.reply_time:
        post.reply_time = payload.reply_time
    if payload.reply_on_comments:
        post.reply_on_comments = payload.reply_on_comments

    post.save()
    return schemas.PostSchema.from_orm(post)


@router.get(
    "/{post_id}",
    response={200: schemas.PostSchema, 404: str}
)
@post_exist
def get_post(request: HttpRequest, post_id: int) -> schemas.PostSchema:
    post = Post.objects.prefetch_related(
        "comments__replies", "author"
    ).get(id=post_id)

    post_schema = schemas.PostSchema.from_orm(post)
    post_schema.comments = schemas.CommentSchema.build_comment_hierarchy(
        post.comments.all()
    )

    return post_schema


@router.patch(
    "/{post_id}",
    response={200: schemas.PostSchema, 403: str, 404: str}, auth=JWTAuth()
)
@post_exist
@has_edit_access
def edit_post(
        request: HttpRequest, post_id: int,
        payload: schemas.UpdatePostSchema
) -> schemas.PostSchema:
    post = Post.objects.get(id=post_id)

    if payload.title is not None:
        post.title = payload.title
    if payload.text is not None:
        post.text = payload.text
    if payload.reply_time is not None:
        post.reply_time = payload.reply_time

    post.save()
    return schemas.PostSchema.from_orm(post)


@router.patch(
    "/{post_id}/toggle",
    response={200: schemas.PostSchema}, auth=JWTAuth()
)
@post_exist
@has_edit_access
def toggle_auto_replay(
        request: HttpRequest, post_id: int
) -> schemas.PostSchema:
    post = Post.objects.get(id=post_id)
    post.reply_on_comments = not post.reply_on_comments

    post.save()
    return schemas.PostSchema.from_orm(post)


@router.delete(
    "/{post_id}",
    response={200: str, 403: str, 404: str}, auth=JWTAuth()
)
@post_exist
@has_delete_access
def delete_post(request: HttpRequest, post_id: int) -> Response:
    post = Post.objects.get(id=post_id)
    post.delete()
    return Response(
        {"detail": "Post deleted successfully"},
        status=status.HTTP_200_OK
    )
