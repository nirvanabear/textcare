from django.shortcuts import render

from chat.models import Room

import environ
# Initialise environment variables
env = environ.Env()
environ.Env.read_env()

def index_view(request):
    return render(request, 'index.html', {
        'rooms': Room.objects.all(),
    })


def room_view(request, room_name):
    chat_room, created = Room.objects.get_or_create(name=room_name)
    # Added to send message in channel from whatsapp views.py
    # Channel.objects.create(channel_name=self.channel_name)
    # logger.debug(dtn + "/chat/ channel name: " + str(f"{self.channel_name}"))

    send_message_url = f"{env('SEND_MESSAGE_URL')}"

    context = {
        'send_message_url': send_message_url,
        'room': chat_room,
    }
    return render(request, 'room.html', context=context)