from ninja_jwt.routers.obtain import obtain_pair_router
from ninja_jwt.routers.verify import verify_router
from ninja import NinjaAPI

api = NinjaAPI()

api.add_router("token/", router=obtain_pair_router)
api.add_router("token/", router=verify_router)
