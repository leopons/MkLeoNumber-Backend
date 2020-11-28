# Generated by Django 3.1.2 on 2020-11-17 18:57

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upsets', '0009_auto_20201117_1832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='set',
            name='looser_characters',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=[], size=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='set',
            name='winner_characters',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), default=[], size=None),
            preserve_default=False,
        ),
    ]
