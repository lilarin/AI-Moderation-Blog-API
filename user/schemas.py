from ninja import (
    Schema,
    Field
)


class UserSchema(Schema):
    id: int
    username: str
    is_staff: bool


class UpdatePasswordSchema(Schema):
    old_password: str
    new_password: str


class CreateUserSchema(Schema):
    username: str = Field(min_length=3, max_length=150)
    password: str
