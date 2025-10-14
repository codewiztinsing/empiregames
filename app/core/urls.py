from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import dashboard
from .main import api

urlpatterns = [
    path('dashboard/',include('dashboard.urls')),
    path('agent/',include('dashboard.agent_urls')),
    path('accounts/',include('users.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
    path('promotions/', include('promotion.urls'), name='promotions'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
