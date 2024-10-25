from functools import wraps
from typing import (
    Callable,
    Any
)

from django.http import HttpRequest
from ninja.errors import HttpError
from ninja_extra import status

from post.models import Post


def post_exist(func):
    @wraps(func)
    def wrapper(
            request: HttpRequest,
            post_id: int, *args, **kwargs
    ) -> Any:
        try:
            Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            raise HttpError(
                status.HTTP_404_NOT_FOUND,
                "Post not found"
            )
        return func(request, post_id, *args, **kwargs)
    return wrapper


def has_edit_access(func: Callable):
    @wraps(func)
    def wrapper(
            request: HttpRequest,
            post_id: int, *args, **kwargs
    ) -> Any:
        post = Post.objects.get(id=post_id)
        if not post.author == request.user:
            raise HttpError(
                status.HTTP_403_FORBIDDEN,
                "You do not have permission to do edit this post"
            )
        return func(request, post_id, *args, **kwargs)
    return wrapper


def has_delete_access(func: Callable):
    @wraps(func)
    def wrapper(
            request: HttpRequest,
            post_id: int, *args, **kwargs
    ) -> Any:
        post = Post.objects.get(id=post_id)
        if not (request.user.is_staff or post.author == request.user):
            raise HttpError(
                status.HTTP_403_FORBIDDEN,
                "You do not have permission to do delete this post"
            )
        return func(request, post_id, *args, **kwargs)
    return wrapper
