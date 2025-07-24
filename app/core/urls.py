from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from .main import api


def game_view(request):
    print("headers ",request.headers)
    if 'Origin' not in request.headers or request.headers['Origin'] != 'wow bot eshetu derege':
        return render(request, '404.html', status=404)
    return render(request, 'build/index.html')

urlpatterns = [
    path('',game_view, name='game_view'),
    path('admin/', admin.site.urls),
    path('api/v1/', api.urls),
    path('', game_view, name='game_view')
]
