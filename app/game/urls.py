from django.urls import path
from . import views, api

app_name ="game"
urlpatterns = [
    path('join-game/', views.index, name='join_game'),
    path("game-details/<int:game_id>/", views.game_details, name='game_details'),
    path('api/fake-player-settings/', api.fake_player_settings, name='fake_player_settings'),
    path('api/fake-player-settings/public/', api.fake_player_settings_public, name='fake_player_settings_public'),
]