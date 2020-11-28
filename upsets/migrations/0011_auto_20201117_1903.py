# Generated by Django 3.1.2 on 2020-11-17 19:03

import django.contrib.postgres.fields
from django.db import migrations, models
import upsets.models


class Migration(migrations.Migration):

    dependencies = [
        ('upsets', '0010_auto_20201117_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='set',
            name='looser_characters',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=upsets.models.empty_array, size=None),
        ),
        migrations.AlterField(
            model_name='set',
            name='winner_characters',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=upsets.models.empty_array, size=None),
        ),
    ]
