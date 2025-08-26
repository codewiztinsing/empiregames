from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from .views import dashboard
from .main import api


def game_view(request):
    return render(request, 'build/index.html')





urlpatterns = [
    path('',game_view, name='game_view'),
    path('dashboard/',dashboard,name = "dashboard"),
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
    path('', game_view, name='game_view')
]
