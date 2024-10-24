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
    username: str = Field(max_length=150)
    password: str
