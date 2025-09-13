from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from .views import dashboard
from .main import api


def game_view(request):
    return render(request, 'build/index.html')

urlpatterns = [
    path('',game_view, name='game_view'),
    path('dashboard/',include('dashboard.urls')),
    path('accounts/',include('users.urls')),
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
    path('', game_view, name='game_view'),
    path('promotions/', include('promotion.urls'), name='promotions'),
    re_path(r'^.*$', game_view, name='game_view'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
