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
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('bingo_cards/', views.bingo_cards, name='bingo_cards'),
    path('messages/', views.dashboard_messages, name='messages'),
    path('contact/', views.contact, name='contact'),
    path('logout/', views.logout, name='logout'),
    
    # Agent Management URLs
    path('agents/', views.agents, name='agents'),
    path('agents/create/', views.create_agent, name='create_agent'),
    path('agents/<int:agent_id>/', views.agent_detail, name='agent_detail'),
    path('agents/<int:agent_id>/edit/', views.edit_agent, name='edit_agent'),
    path('agents/<int:agent_id>/delete/', views.delete_agent, name='delete_agent'),
    path('api/users-with-agents/', views.users_with_agents_api, name='users_with_agents_api'),
]