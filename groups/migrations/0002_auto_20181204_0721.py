# Generated by Django 2.1.3 on 2018-12-04 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companygroup',
            old_name='group',
            new_name='linked_group',
        ),
    ]