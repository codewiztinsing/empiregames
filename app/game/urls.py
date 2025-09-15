from django.urls import path
from . import views

app_name ="game"
urlpatterns = [
    path('join-game/', views.index, name='join_game'),
    path("game-details/<int:game_id>/", views.game_details, name='game_details'),
]