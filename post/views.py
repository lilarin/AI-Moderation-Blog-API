from django.http import HttpRequest
from ninja import Router
from ninja.responses import Response
from ninja.pagination import (
    paginate,
    PageNumberPagination
)
from ninja_extra import status
from ninja_jwt.authentication import JWTAuth

from social_service.settings import PAGE_PAGINATION_NUMBER
from post.decorators import (
    post_exist,
    has_delete_access,
    has_edit_access
)
from post.models import Post
from post.schemas import (
    PostSchema,
    CommentSchema,
    CreatePostSchema,
    UpdatePostSchema
)

router = Router()


@router.get("", response=list[PostSchema])
@paginate(PageNumberPagination, page_size=PAGE_PAGINATION_NUMBER)
def get_posts(request: HttpRequest) -> list[PostSchema]:
    posts = Post.objects.all()
    post_schemas = []

    for post in posts:
        post_schema = PostSchema.from_orm(post)
        post_schema.comments = [
            CommentSchema.from_orm(comment)
            for comment in post.comments.all()
        ]
        post_schemas.append(post_schema)

    return post_schemas


@router.post(
    "",
    response={200: PostSchema, 400: str},
    auth=JWTAuth()
)
def create_post(
        request: HttpRequest, payload: CreatePostSchema
) -> PostSchema:
    post = Post(
        author=request.user,
        title=payload.title,
        text=payload.text,
        reply_time=payload.reply_time
    )
    post.save()
    return PostSchema.from_orm(post)


@router.get(
    "/{post_id}",
    response={200: PostSchema, 404: str}
)
@post_exist
def get_post(request: HttpRequest, post_id: int) -> PostSchema:
    post = Post.objects.get(id=post_id)
    return post


@router.patch(
    "/{post_id}",
    response={200: PostSchema, 403: str, 404: str}, auth=JWTAuth()
)
@post_exist
@has_edit_access
def edit_post(
        request: HttpRequest, post_id: int,
        payload: UpdatePostSchema
) -> PostSchema:
    post = Post.objects.get(id=post_id)

    if payload.title is not None:
        post.title = payload.title
    if payload.text is not None:
        post.text = payload.text
    if payload.reply_time is not None:
        post.reply_time = payload.reply_time

    post.save()
    return PostSchema.from_orm(post)


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