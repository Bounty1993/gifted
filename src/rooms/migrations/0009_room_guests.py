# Generated by Django 2.2.1 on 2019-05-31 23:35

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rooms', '0008_auto_20190531_1730'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='guests',
            field=models.ManyToManyField(blank=True, related_name='guest_rooms', to=settings.AUTH_USER_MODEL),
        ),
    ]
