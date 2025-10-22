from django.urls import path
from django.views.generic import RedirectView
from . import views


app_name = 'dashboard'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('game_rooms/', views.game_rooms, name='game_rooms'),
    path('game_rooms/<int:game_room_id>/', views.game_room_detail, name='game_room_detail'),
    # Backward compatibility
    path('game_types/', views.game_rooms, name='game_types'),
    path('game_types/<int:game_type_id>/', views.game_room_detail, name='game_type_detail'),
    path('games/', views.games, name='games'),
    path('game-settings/', views.game_settings, name='game_settings'),
    path('payments/', views.payments, name='payments'),
    path('transcations/', views.transcations, name='transcations'),
    path('users/', views.users, name='users'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/details/', views.user_details, name='user_details'),
    path('users/create/', views.user_create, name='user_create'),
    # Backward-compat: if any template still references bingo_cards, send users to dashboard
    # Referrals URL removed
    path('messages/', views.messages_view, name='messages'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout_view, name='logout'),
    path('withdrawal-requests/<int:request_id>/approve/', views.approve_withdrawal_request, name='approve_withdrawal_request'),
    path('withdrawal-requests/<int:request_id>/reject/', views.reject_withdrawal_request, name='reject_withdrawal_request'),
    path('manual-deposits/add/', views.add_manual_deposit, name='add_manual_deposit'),
    
    # Referral bonus management URLs removed
    
    # Roles management
    path('roles/', views.roles, name='roles'),
    path('roles/create/', views.create_role, name='create_role'),
    path('roles/<int:user_id>/assign/', views.assign_role, name='assign_role'),
    path('roles/<int:user_id>/remove/', views.remove_role, name='remove_role'),
    ]