from ninja import NinjaAPI
from users.auth import JWTAuth
from ninja_simple_jwt.auth.views.api import mobile_auth_router, web_auth_router
from wallet.api import router as wallet_router
from users.api import users_router
from game.api import game_router
from webhooks.api import webhooks_router
from users.referral_api import router as referral_router
from promotion.api import promotion_router
# base api with global JWT protection
api = NinjaAPI(auth=JWTAuth())

# Debug middleware to log Authorization header for wallet balance route
from django.utils.deprecation import MiddlewareMixin

class DebugAuthHeaderMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            path = request.path or ''
            if '/api/v1/wallet/player/' in path:
                auth = request.META.get('HTTP_AUTHORIZATION')
                print('[AuthHeaderDebug] path=', path, 'auth_present=', bool(auth), 'auth_prefix=', (auth[:24] if auth else None))
        except Exception:
            pass

try:
    from django.conf import settings
    if hasattr(settings, 'MIDDLEWARE'):
        settings.MIDDLEWARE = list(settings.MIDDLEWARE) + [
            'core.main.DebugAuthHeaderMiddleware'
        ]
except Exception:
    pass

# api for users
api.add_router("/users", users_router)
api.add_router("/wallet/", wallet_router)
api.add_router("/game/", game_router)
api.add_router("/webhooks/", webhooks_router)
api.add_router("/referrals/", referral_router)
api.add_router("/promotions/", promotion_router)
