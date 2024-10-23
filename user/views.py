from ninja_jwt.authentication import JWTAuth
from ninja import Router

from user.schemas import UserSchema

router = Router()


@router.get("", response=UserSchema, auth=JWTAuth())
def get_user(request):
    return UserSchema.from_orm(request.user)