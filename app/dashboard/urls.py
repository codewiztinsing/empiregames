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
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/details/', views.user_details, name='user_details'),
    path('bingo_cards/', views.bingo_cards, name='bingo_cards'),
    path('referrals/', views.referrals, name='referrals'),
    path('messages/', views.messages_view, name='messages'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout_view, name='logout'),
    path('withdrawal-requests/<int:request_id>/approve/', views.approve_withdrawal_request, name='approve_withdrawal_request'),
    path('withdrawal-requests/<int:request_id>/reject/', views.reject_withdrawal_request, name='reject_withdrawal_request'),
    path('manual-deposits/add/', views.add_manual_deposit, name='add_manual_deposit'),
    
    # Referral bonus management URLs
    path('unwithdrawable-bonuses/', views.unwithdrawable_bonuses, name='unwithdrawable_bonuses'),
    path('users/<int:user_id>/move-bonus/', views.move_bonus_to_earnings, name='move_bonus_to_earnings'),
    path('referral-bonuses/', views.referral_bonuses, name='referral_bonuses'),
    path('referral-bonuses/<int:bonus_id>/approve/', views.approve_referral_bonus, name='approve_referral_bonus'),
    path('referral-bonuses/<int:bonus_id>/reject/', views.reject_referral_bonus, name='reject_referral_bonus'),
    path('referral-bonuses/bulk-approve/', views.bulk_approve_bonuses, name='bulk_approve_bonuses'),
    path('process-tuesday-bonuses/', views.process_tuesday_bonuses, name='process_tuesday_bonuses'),
    path('fake-players-settings/', views.fake_players_settings_view, name='fake_players_settings'),
    ]