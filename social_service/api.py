from ninja_jwt.routers.obtain import obtain_pair_router
from ninja_jwt.routers.verify import verify_router
from ninja import NinjaAPI

from user.views import router as user_router
from post.views import router as post_router
from comment.views import router as comment_router

api = NinjaAPI()

api.add_router("user/token/", router=obtain_pair_router, tags=["user"])
api.add_router("user/token/", router=verify_router, tags=["user"])
api.add_router("user/", router=user_router, tags=["user"])
api.add_router("posts/", router=post_router, tags=["posts"])
api.add_router("comments/", router=comment_router, tags=["comments"])
