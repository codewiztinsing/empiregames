from django.urls import path
from . import views

urlpatterns = [
    path('', views.chapa_callback, name='chapa_callback'),
]