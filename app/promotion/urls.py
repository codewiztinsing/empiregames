from django.urls import path
from . import views


app_name = 'promotions'
urlpatterns = [
    path('upload_banner/', views.upload_banner, name='upload_banner'),
]