from django.urls import path
from . import views

urlpatterns = [
    path('', views.export_play_data_to_csv, name='export_play_data_to_csv'),
]
