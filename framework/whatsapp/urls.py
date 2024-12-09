from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('send_message/', views.send_message, name='send_message'),
    path('chat/open_chat/', views.open_chat, name='open_chat'),
    path('previous_send_message/', views.previous_send_message, name='previous_send_message'),
    path('set_chat/', views.set_chat, name='set_chat'),
    path('end_session/', views.end_session, name='end_session'),
    # path('chatgpt/', views.reply, name='chatgpt'),
]