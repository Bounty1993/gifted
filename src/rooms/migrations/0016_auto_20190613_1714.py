# Generated by Django 2.2.1 on 2019-06-13 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0015_auto_20190609_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='score',
            field=models.FloatField(),
        ),
    ]