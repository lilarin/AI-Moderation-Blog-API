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

from user.decorators import (
    change_password_validation,
    username_availability
)
import user.schemas as schemas

router = Router()


@router.get("", response=schemas.UserSchema, auth=JWTAuth())
def get_user(request: HttpRequest) -> schemas.UserSchema:
    return schemas.UserSchema.from_orm(request.user)


@router.patch("", auth=JWTAuth())
@change_password_validation
def update_password(
        request: HttpRequest, payload: schemas.UpdatePasswordSchema
) -> Response:
    user = request.user

    user.set_password(payload.new_password)
    user.save()
    return Response(
        {"detail": "Password has been successfully updated"},
        status=status.HTTP_200_OK
    )


@router.post("/register", response=schemas.UserSchema)
@username_availability
def register_user(
        request: HttpRequest, payload: schemas.CreateUserSchema
) -> schemas.UserSchema:
    try:
        validate_password(payload.password)
    except ValidationError as error:
        raise HttpError(
            400,
            " ".join(error.messages)
        )

    with transaction.atomic():
        user = get_user_model().objects.create_user(
            username=payload.username
        )
        user.set_password(payload.password)
    return schemas.UserSchema.from_orm(user)
