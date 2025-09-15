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
    path('messages/', views.messages_view, name='messages'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout_view, name='logout'),
    path('withdrawal-requests/<int:request_id>/approve/', views.approve_withdrawal_request, name='approve_withdrawal_request'),
    path('withdrawal-requests/<int:request_id>/reject/', views.reject_withdrawal_request, name='reject_withdrawal_request'),
    ]