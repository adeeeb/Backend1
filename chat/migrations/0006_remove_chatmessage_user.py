# Generated by Django 5.1.6 on 2025-02-23 23:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_chatmessage_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatmessage',
            name='user',
        ),
    ]
