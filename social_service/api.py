from ninja_jwt.routers.obtain import obtain_pair_router
from ninja_jwt.routers.verify import verify_router
from ninja import NinjaAPI

from user.views import router as user_router
from post.views import router as post_router

api = NinjaAPI()

api.add_router("token/", router=obtain_pair_router)
api.add_router("token/", router=verify_router)
api.add_router("user/", router=user_router)
api.add_router("posts/", router=post_router)
