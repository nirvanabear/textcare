from django.urls import re_path

from . import consumers


whatsapp_urlpatterns = [
    re_path(r'ws/whatsapp/(?P<phone_num>\w+)/$', consumers.WhatsappConsumer.as_asgi()),
]
