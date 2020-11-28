# Generated by Django 3.1.2 on 2020-11-01 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upsets', '0003_auto_20201101_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='set',
            name='original_id',
            field=models.CharField(default=0, max_length=1000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='set',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='set',
            name='looser_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='set',
            name='round_name',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='set',
            name='winner_score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]