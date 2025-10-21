from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from .views import dashboard
from .main import api

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboard/', permanent=False), name='index'),
    path('dashboard/',include('dashboard.urls')),
    path('accounts/',include('users.urls'),name='accounts'),
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
    path('game/', include('game.urls'), name='game'),
    path('wallet/', include('wallet.urls'), name='wallet')
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
