from django.urls import path
from . import views

app_name ="game"
urlpatterns = [
    path('join-game/', views.index, name='join_game'),
]