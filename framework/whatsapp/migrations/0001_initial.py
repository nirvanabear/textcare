# Generated by Django 5.1.3 on 2025-01-06 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=15)),
                ('message', models.CharField(max_length=2000)),
                ('response', models.CharField(max_length=2000)),
            ],
        ),
    ]
