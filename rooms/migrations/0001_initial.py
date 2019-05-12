# Generated by Django 2.2.1 on 2019-05-02 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
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
            ],
        ),
    ]