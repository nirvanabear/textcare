# Generated by Django 5.1.3 on 2025-01-09 06:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('whatsapp', '0002_chatsession_clientlog_chatlog_chatsession_phone_num'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientlog',
            name='waitlist',
        ),
    ]
