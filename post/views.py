from functools import wraps

from ninja import Router
from ninja.errors import HttpError
from ninja.responses import Response
from ninja_extra import status
from ninja_jwt.authentication import JWTAuth
from pydantic import ValidationError
from post.schemas import PostSchema, CommentSchema, CreatePostSchema
from post.models import Post

router = Router()


@router.get("", response=list[PostSchema])
def get_posts(request):
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


@router.post("/create", response=PostSchema, auth=JWTAuth())
def register_user(request, payload: CreatePostSchema):
    print(request.user.is_authenticated)
    try:
        post = Post(
            author=request.user,
            title=payload.title,
            text=payload.text,
            reply_time=payload.reply_time
        )
        post.save()
        return PostSchema.from_orm(post)
    except ValidationError as error:
        raise HttpError(400, " ".join(error.messages))


def has_access(func):
    @wraps(func)
    def wrapper(request, post_id, *args, **kwargs):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise HttpError(
                status.HTTP_404_NOT_FOUND,
                "Post not found"
            )
        if not (request.user.is_staff or post.author == request.user):
            raise HttpError(
                status.HTTP_403_FORBIDDEN,
                "You do not have permission to delete this post")

        return func(request, post_id, *args, **kwargs)
    return wrapper


@router.delete("/{post_id}", auth=JWTAuth())
@has_access
def delete_post(request, post_id: int):
    post = Post.objects.get(id=post_id)
    post.delete()
    return Response(
        {"detail": "Post deleted successfully"},
        status=status.HTTP_200_OK
    )