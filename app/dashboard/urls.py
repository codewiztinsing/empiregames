from django.urls import path
from . import views


app_name = 'dashboard'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('game_types/', views.game_types, name='game_types'),
    path('game_types/<int:game_type_id>/', views.game_type_detail, name='game_type_detail'),
    path('games/', views.games, name='games'),
    path('payments/', views.payments, name='payments'),
    path('transcations/', views.transcations, name='transcations'),
    path('users/', views.users, name='users'),
    path('bingo_cards/', views.bingo_cards, name='bingo_cards'),
    path('referrals/', views.referrals, name='referrals'),
    path('messages/', views.messages, name='messages'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout, name='logout'),
]