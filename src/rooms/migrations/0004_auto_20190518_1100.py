# Generated by Django 2.2.1 on 2019-05-18 11:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_auto_20190518_0746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donations', to='rooms.Room'),
        ),
    ]