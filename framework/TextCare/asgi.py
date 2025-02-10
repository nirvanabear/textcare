"""
ASGI config for TextCare project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TextCare.settings')

django.setup()

from websox.routing import websox_urlpatterns
from chat.routing import chat_urlpatterns
from whatsapp.routing import whatsapp_urlpatterns

from django.core.asgi import get_asgi_application


# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })

application = ProtocolTypeRouter({
  'http': get_asgi_application(),
  'websocket': URLRouter(
      websox_urlpatterns + chat_urlpatterns + whatsapp_urlpatterns
    ),
})

#############

# import os

# from channels.routing import ProtocolTypeRouter
# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TextCare.settings')

# application = ProtocolTypeRouter({
#   'http': get_asgi_application(),
# })
