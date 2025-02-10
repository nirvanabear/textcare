from django.contrib.auth.models import User
from django.db import models
import uuid

from datetime import datetime


class Conversation(models.Model):
    sender = models.CharField(max_length=15)
    message = models.CharField(max_length=2000)
    response = models.CharField(max_length=2000)
    paginate_by = 10


######


class ClientLog(models.Model):
    phone_num = models.CharField(primary_key=True, help_text="Phone number of incoming messages")
    state = models.IntegerField(default=20, help_text="Status of a client as they move through session pipeline")
    paginate_by = 10

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.phone_num


class ChatSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for a particular chat session")
    client = models.ForeignKey(ClientLog, on_delete=models.RESTRICT, null=True, help_text="Phone number for incoming messages")
    start_time = models.DateTimeField(help_text="Start time for a particular chat session")
    open_session = models.BooleanField(default=True, help_text="Is this session currently open?")
    paginate_by = 10

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        # return f'{self.session_id}'
        return self.session_id


class ChatLog(models.Model):
    '''List of all incoming and outgoing messages.'''
    message = models.TextField(help_text="Message received or sent")
    session = models.ForeignKey(ChatSession, on_delete=models.RESTRICT, null=True, help_text="Unique ID for a particular chat session")
    timestamp = models.DateTimeField(auto_now_add=True)
    paginate_by = 10

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.message


######


class Room(models.Model):
    name = models.CharField(max_length=128)
    # online = models.ManyToManyField(to=User, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # def get_online_count(self):
    #     return self.online.count()

    # def join(self, user):
    #     self.online.add(user)
    #     self.save()

    # def leave(self, user):
    #     self.online.remove(user)
    #     self.save()

    

    def __str__(self):
        return f'{self.name} ({self.get_online_count()})'


class Message(models.Model):
    # user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    room = models.ForeignKey(to=Room, on_delete=models.CASCADE)
    content = models.CharField(max_length=512)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content} [{self.timestamp}]'

class Channel(models.Model):
    channel_name = models.CharField(max_length=128)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.channel_name}: [{self.timestamp}]'