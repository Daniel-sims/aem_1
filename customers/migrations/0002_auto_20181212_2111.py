# Generated by Django 2.1.3 on 2018-12-12 21:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='company',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='customer_id',
        ),
    ]