# Generated by Django 4.0.3 on 2022-05-15 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_alter_auction_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='photo',
            field=models.URLField(max_length=500),
        ),
    ]