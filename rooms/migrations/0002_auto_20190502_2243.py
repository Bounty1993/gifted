# Generated by Django 2.2.1 on 2019-05-02 22:43

import datetime
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='date_expires',
            field=models.DateField(default=datetime.date(2019, 5, 3)),
        ),
        migrations.AddField(
            model_name='room',
            name='patrons',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]