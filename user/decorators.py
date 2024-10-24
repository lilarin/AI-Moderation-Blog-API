from functools import wraps
from typing import (
    Callable,
    Any
)

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.http import HttpRequest
from django.core.exceptions import ValidationError
from ninja.errors import HttpError

from user.schemas import (
    CreateUserSchema,
    UpdatePasswordSchema
)


def change_password_validation(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(
            request: HttpRequest,
            payload: UpdatePasswordSchema, *args, **kwargs
    ) -> Any:
        user = request.user
        new_password = payload.new_password
        old_password = payload.old_password

        if new_password == old_password:
            raise HttpError(
                400,
                "New password must be different from current password"
            )
        if not user.check_password(old_password):
            raise HttpError(
                400,
                "Current password is incorrect."
            )

        try:
            validate_password(new_password)
        except ValidationError as error:
            raise HttpError(
                400,
                " ".join(error.messages)
            )

        return func(request, payload, *args, **kwargs)
    return wrapper

def username_availability(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(
            request: HttpRequest,
            payload: CreateUserSchema, *args, **kwargs
    ) -> Any:
        User = get_user_model()
        if User.objects.filter(username=payload.username).exists():
            raise HttpError(
                400,
                "Username is already taken."
            )
        return func(request, payload, *args, **kwargs)
    return wrapper
