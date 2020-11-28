# Generated by Django 3.1.2 on 2020-10-31 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upsets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='id',
            field=models.CharField(max_length=1000, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='player',
            name='tag',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='set',
            name='round_name',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='id',
            field=models.CharField(max_length=1000, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='name',
            field=models.CharField(max_length=1000),
        ),
    ]