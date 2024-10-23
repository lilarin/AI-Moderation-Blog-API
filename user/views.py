from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja import Router
from functools import wraps

from user.schemas import (
    UserSchema,
    UpdatePasswordSchema,
    RegisterUserSchema
)

router = Router()


@router.get("", response=UserSchema, auth=JWTAuth())
def get_user(request):
    return UserSchema.from_orm(request.user)


def password_validation(func):
    @wraps(func)
    def wrapper(request, payload, *args, **kwargs):
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
def update_profile(request, payload: UpdatePasswordSchema):
    user = request.user

    user.set_password(payload.new_password)
    user.save()
    return {"message": "Password has been successfully updated"}


def username_availability(func):
    @wraps(func)
    def wrapper(request, payload, *args, **kwargs):
        if get_user_model().objects.filter(username=payload.username).exists():
            raise HttpError(
                400,
                "Username is already taken."
            )
        return func(request, payload, *args, **kwargs)

    return wrapper


@router.post("/register", response=UserSchema)
@username_availability
def register_user(request, payload: RegisterUserSchema):
    try:
        validate_password(payload.password)
        with transaction.atomic():
            user = get_user_model().objects.create_user(username=payload.username)
            user.set_password(payload.password)
            user.save()
        return UserSchema.from_orm(user)
    except ValidationError as error:
        raise HttpError(400, " ".join(error.messages))
