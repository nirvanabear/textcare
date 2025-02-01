from django.db import models
import uuid


class Conversation(models.Model):
    sender = models.CharField(max_length=15)
    message = models.CharField(max_length=2000)
    response = models.CharField(max_length=2000)
    paginate_by = 10

        # try:
        #     with transaction.atomic():
        #             conversation = Conversation.objects.create(
        #                 sender=whatsapp_number,
        #                 message=body,
        #                 response=chatgpt_response
        #             )
        #             conversation.save()
        #             logger.info(f"Conversation #{conversation.id} stored in database")
        # except Exception as e:
        #     logger.error(f"Error storing conversation in database: {e}")


######


class ClientLog(models.Model):
    phone_num = models.CharField(primary_key=True, help_text="Phone number of incoming messages")
    state = models.IntegerField(default=20, help_text="Status of a client as they move through session pipeline")
    # waitlist = models.BooleanField(default=False)
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