from django.urls import path
from . import api as views

urlpatterns = [
    path('', views.callbacks_disabled, name='callbacks_disabled'),
]