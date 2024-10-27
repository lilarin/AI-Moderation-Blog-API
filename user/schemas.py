from ninja import (
    Schema,
    Field
)


class BaseUserSchema(Schema):
    username: str = Field(min_length=3, max_length=150)


class UserSchema(BaseUserSchema):
    id: int
    is_staff: bool


class CreateUserSchema(BaseUserSchema):
    password: str


class UpdatePasswordSchema(Schema):
    old_password: str
    new_password: str
