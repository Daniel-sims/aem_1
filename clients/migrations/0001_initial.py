# Generated by Django 2.1.3 on 2018-11-26 21:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('client_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('customer_count', models.IntegerField(default=0)),
                ('fully_comp_count', models.IntegerField(default=0)),
                ('basic_cover_count', models.IntegerField(default=0)),
            ],
        ),
    ]
