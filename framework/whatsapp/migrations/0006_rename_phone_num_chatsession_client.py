# Generated by Django 5.1.3 on 2025-01-12 06:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('whatsapp', '0005_alter_chatlog_options_chatsession_open_session'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chatsession',
            old_name='phone_num',
            new_name='client',
        ),
    ]