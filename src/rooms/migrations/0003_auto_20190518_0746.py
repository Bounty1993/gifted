# Generated by Django 2.2.1 on 2019-05-18 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0002_auto_20190514_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='comment',
            field=models.CharField(blank=True, max_length=250),
        ),
    ]