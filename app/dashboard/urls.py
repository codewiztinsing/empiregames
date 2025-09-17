from django.urls import path
from . import views


app_name = 'dashboard'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('game_types/', views.game_types, name='game_types'),
    path('game_types/<int:game_type_id>/', views.game_type_detail, name='game_type_detail'),
    path('games/', views.games, name='games'),
    path('payments/', views.payments, name='payments'),
    path('transactions/', views.transcations, name='transactions'),
    path('users/', views.users, name='users'),
    path('bingo_cards/', views.bingo_cards, name='bingo_cards'),
    path('referrals/', views.referrals, name='referrals'),
    path('messages/', views.messages_view, name='messages'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout_view, name='logout'),
    path('withdrawal-requests/<int:request_id>/approve/', views.approve_withdrawal_request, name='approve_withdrawal_request'),
    path('withdrawal-requests/<int:request_id>/reject/', views.reject_withdrawal_request, name='reject_withdrawal_request'),
    # Message API endpoints
    path('api/broadcast-message/', views.broadcast_message_api, name='broadcast_message_api'),
    path('api/message-progress/<int:broadcast_id>/', views.message_progress_api, name='message_progress_api'),
    path('api/broadcast-details/<int:broadcast_id>/', views.broadcast_details_api, name='broadcast_details_api'),
    path('api/resend-broadcast/<int:broadcast_id>/', views.resend_broadcast_api, name='resend_broadcast_api'),
    path('api/cancel-broadcast/<int:broadcast_id>/', views.cancel_broadcast_api, name='cancel_broadcast_api'),
    # Contact API endpoints
    path('api/contacts/', views.contacts_api, name='contacts_api'),
    path('api/contacts/<int:contact_id>/', views.contact_detail_api, name='contact_detail_api'),
    path('api/contacts/<int:contact_id>/toggle-status/', views.toggle_contact_status_api, name='toggle_contact_status_api'),
    ]