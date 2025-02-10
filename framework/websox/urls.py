from django.urls import path
from . import views

urlpatterns = [
    path('wshome/', views.wshome, name='wshome'),
]   