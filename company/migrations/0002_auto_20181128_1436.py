# Generated by Django 2.1.3 on 2018-11-28 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]