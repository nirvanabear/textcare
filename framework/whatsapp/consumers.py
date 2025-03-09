import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import ClientLog, ChatSession, ChatLog, Room, Channel

import logging
from datetime import datetime
logger = logging.getLogger('django')
dtn = datetime.now().strftime('%Y-%m-%d %H:%M') + " "


class WhatsappConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.phone_num = None
        self.session_group_name = None
        self.session = None

    def connect(self):
        self.phone_num = self.scope['url_route']['kwargs']['phone_num']
        self.session_group_name = f'chat_{self.phone_num}'
        logger.debug("/whatsapp/ consumer test")

        self.client, self.create_client = ClientLog.objects.get_or_create(
            phone_num=self.phone_num
        )
        logger.debug(f"{self.phone_num}")

        try:
            self.session = ChatSession.objects.filter(client__phone_num=self.phone_num, open_session=True).latest('start_time')
        except:
            self.session = ChatSession.objects.get_or_create(client=self.client)
            logger.exception("Get or Create Sesssion")
            logger.exception(f"{self.session}")
        logger.debug(f"{self.session}")
        # Added to send message in channel from whatsapp views.py
        try:
            Channel.objects.get_or_create(channel_name=self.channel_name, session=self.session)
        except:
            logger.exception(dtn + "/whatsapp/ channel name: " + str(f"{self.channel_name}"))

        # connection has to be accepted
        self.accept()

        # join the session group
        async_to_sync(self.channel_layer.group_add)(
            self.session_group_name,
            self.channel_name,
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.session_group_name,
            self.channel_name,
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Maybe trigger database insert?
        # Then database query, to be pushed to channel.

        # send chat message event to the session
        async_to_sync(self.channel_layer.group_send)(
            self.session_group_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))