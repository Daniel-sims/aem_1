# Generated by Django 2.1.3 on 2018-12-23 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0002_remove_company_company_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyModule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('slug_field', models.SlugField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
