from functools import wraps
from typing import (
    Callable,
    Any
)

from django.http import HttpRequest
from ninja.errors import HttpError
from ninja_extra import status

from comment.models import Comment


def comment_exist(func):
    @wraps(func)
    def wrapper(
            request: HttpRequest,
            comment_id: int, *args, **kwargs
    ) -> Any:
        try:
            Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise HttpError(
                status.HTTP_404_NOT_FOUND,
                "Comment not found"
            )
        return func(request, comment_id, *args, **kwargs)
    return wrapper


def has_edit_access(func: Callable):
    @wraps(func)
    def wrapper(
            request: HttpRequest,
            comment_id: int, *args, **kwargs
    ) -> Any:
        comment = Comment.objects.get(id=comment_id)
        if not comment.author == request.user:
            raise HttpError(
                status.HTTP_403_FORBIDDEN,
                "You do not have permission to do edit this comment"
            )
        return func(request, comment_id, *args, **kwargs)
    return wrapper


def has_delete_access(func: Callable):
    @wraps(func)
    def wrapper(
            request: HttpRequest,
            comment_id: int, *args, **kwargs
    ) -> Any:
        comment = Comment.objects.get(id=comment_id)
        if not (request.user.is_staff or comment.author == request.user):
            raise HttpError(
                status.HTTP_403_FORBIDDEN,
                "You do not have permission to delete this comment"
            )
        return func(request, comment_id, *args, **kwargs)
    return wrapper