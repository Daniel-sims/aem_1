# Generated by Django 2.1.3 on 2018-11-29 20:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aemauthentication', '0006_user_user_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='user_type',
        ),
    ]
