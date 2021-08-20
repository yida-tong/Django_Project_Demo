from django.urls import path
from . import views

app_name = 'mysite'

urlpatterns = [
    path('index', views.index, name='index'),
]