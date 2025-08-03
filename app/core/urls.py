from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from .main import api
from .views import dashboard_view

def game_view(request):
    return render(request, 'build/index.html')


urlpatterns = [
    path('',game_view, name='game_view'),
    path('dashboard/',dashboard_view, name='dashboard_view'),
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
    path('', game_view, name='game_view')
]
