from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest
from ninja.errors import HttpError
from ninja.responses import Response
from ninja_extra import status
from ninja_jwt.authentication import JWTAuth
from ninja import Router
from functools import wraps
from typing import Callable

from user.schemas import (
    UserSchema,
    UpdatePasswordSchema,
    CreateUserSchema
)

User = get_user_model()
router = Router()

@router.get("", response=UserSchema, auth=JWTAuth())
def get_user(request: HttpRequest) -> Response:
    return Response(
        UserSchema.from_orm(request.user),
        status=status.HTTP_200_OK
    )

def password_validation(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(
            request: HttpRequest,
            payload: UpdatePasswordSchema, *args, **kwargs
    ) -> Response:
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

@router.patch("", auth=JWTAuth())
@password_validation
def update_password(
        request: HttpRequest, payload: UpdatePasswordSchema
) -> Response:
    user = request.user

    user.set_password(payload.new_password)
    user.save()
    return Response(
        {"message": "Password has been successfully updated"},
        status=status.HTTP_200_OK
    )

def username_availability(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(
            request: HttpRequest,
            payload: CreateUserSchema, *args, **kwargs
    ) -> Response:
        if User.objects.filter(username=payload.username).exists():
            raise HttpError(
                400,
                "Username is already taken."
            )
        return func(request, payload, *args, **kwargs)

    return wrapper

@router.post("/register", response=UserSchema)
@username_availability
def register_user(
        request: HttpRequest, payload: CreateUserSchema
) -> Response:
    try:
        validate_password(payload.password)
        with transaction.atomic():
            user = User.objects.create_user(username=payload.username)
            user.set_password(payload.password)
            user.save()
        return Response(
            UserSchema.from_orm(user),
            status=status.HTTP_200_OK
        )
    except ValidationError as error:
        raise HttpError(400, " ".join(error.messages))
