# Generated by Django 2.2.1 on 2019-05-14 20:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='donation',
            old_name='profile',
            new_name='user',
        ),
    ]
