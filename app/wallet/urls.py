from django.urls import path
from . import views

app_name = 'wallet'
urlpatterns = [
    path('transaction/<int:transaction_id>/', views.transaction_details, name='transaction_details'),
]