from ninja import NinjaAPI
from wallet.api import router as wallet_router
from users.api import users_router
from game.api import game_router,dashboard_router
# base api
api = NinjaAPI()

# api for users
api.add_router("/users/", users_router)
api.add_router("/wallet/", wallet_router)
api.add_router("/game/", game_router)
api.add_router("/dashboard/", dashboard_router)
