# Generated by Django 2.1.3 on 2018-12-11 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0003_auto_20181211_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='client_id',
            field=models.UUIDField(editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
