from django.urls import re_path

from . import consumers
import logging
logger = logging.getLogger('django')

logger.debug('Routing Not Loaded')

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]


logger.debug('Routing Loaded OK')