# Generated by Django 2.2.1 on 2019-05-13 20:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11)),
                ('comment', models.CharField(blank=True, max_length=50)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver', models.CharField(max_length=50)),
                ('gift', models.CharField(max_length=50)),
                ('price', models.DecimalField(decimal_places=2, max_digits=11)),
                ('description', models.CharField(max_length=250)),
                ('to_collect', models.DecimalField(decimal_places=2, max_digits=11)),
                ('visible', models.BooleanField()),
                ('date_expires', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('patrons', models.ManyToManyField(blank=True, through='rooms.Donation', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='donation',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rooms.Room'),
        ),
    ]
