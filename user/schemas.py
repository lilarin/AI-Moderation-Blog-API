from django.contrib.auth import get_user_model
from ninja import (
    Schema,
    ModelSchema,
    Field
)


class UserSchema(ModelSchema):
    class Meta:
        model = get_user_model()
        fields = ["id", "username"]
        write_only_fields = ["password"]


class UpdatePasswordSchema(Schema):
    old_password: str
    new_password: str


class RegisterUserSchema(Schema):
    username: str = Field(max_length=150)
    password: str
