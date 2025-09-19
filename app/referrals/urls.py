from django.urls import path
from . import views

app_name = 'referrals'

urlpatterns = [
    path('', views.referrals_dashboard, name='dashboard'),
    path('bonuses/', views.referral_bonuses, name='bonuses'),
    path('withdrawals/', views.withdrawal_requests, name='withdrawals'),
    path('tree/', views.referral_tree, name='tree'),
    path('api/request-withdrawal/', views.request_withdrawal, name='request_withdrawal'),
    path('api/change-sponsor/', views.change_sponsor, name='change_sponsor'),
]
