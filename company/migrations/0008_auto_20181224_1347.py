# Generated by Django 2.1.3 on 2018-12-24 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0007_auto_20181224_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='modules',
            field=models.ManyToManyField(to='company.CompanyModule'),
        ),
    ]
