from ninja_jwt.routers.obtain import obtain_pair_router
from ninja_jwt.routers.verify import verify_router
from ninja import NinjaAPI
from user.views import router as user_router

api = NinjaAPI()

api.add_router("token/", router=obtain_pair_router)
api.add_router("token/", router=verify_router)
api.add_router("user/", router=user_router)
