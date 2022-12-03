# Generated by Django 4.1 on 2022-10-14 11:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0016_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='description',
            field=models.TextField(blank=True, max_length=1024, null=True, validators=[django.core.validators.MaxLengthValidator(1024)]),
        ),
        migrations.AlterField(
            model_name='listing',
            name='title',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
