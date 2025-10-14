from django.urls import path
from . import agent_views

app_name = 'agent'
urlpatterns = [
    # Authentication
    path('login/', agent_views.agent_login, name='login'),
    path('logout/', agent_views.agent_logout, name='logout'),
    
    # Dashboard
    path('', agent_views.agent_dashboard, name='dashboard'),
    path('dashboard/', agent_views.agent_dashboard, name='dashboard'),
    
    # User Management
    path('users/', agent_views.agent_users, name='users'),
    path('users/<int:user_id>/', agent_views.agent_user_detail, name='user_detail'),
    
    # Commissions
    path('commissions/', agent_views.agent_commissions, name='commissions'),
    
    # Profile
    path('profile/', agent_views.agent_profile, name='profile'),
    path('change-password/', agent_views.agent_change_password, name='change_password'),
]
