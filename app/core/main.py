from ninja import NinjaAPI
from ninja_simple_jwt.auth.views.api import mobile_auth_router, web_auth_router
from wallet.api import router as wallet_router
from users.api import users_router

# base api
api = NinjaAPI()

# api for users
api.add_router("/users/", users_router)
api.add_router("/wallet/", wallet_router)
