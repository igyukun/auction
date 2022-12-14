# Generated by Django 4.1 on 2022-10-05 08:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_remove_comment_listing_remove_comment_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.CharField(max_length=1024, null=True)),
                ('starting_bid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('image', models.ImageField(upload_to='images/%Y/%m/%d/')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='auctions.category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='listing_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
