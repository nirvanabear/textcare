from django.urls import re_path

from . import consumers


# ?P<name> creates a name for the capture group.
# \w+ matches all Unicode alphanumerics and _.
chat_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]

