# Generated by Django 2.2.1 on 2019-06-19 14:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0017_auto_20190613_1728'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='donation',
            options={'ordering': ['date']},
        ),
    ]
