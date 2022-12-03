# Generated by Django 4.1 on 2022-10-17 14:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0017_alter_listing_description_alter_listing_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listing_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
