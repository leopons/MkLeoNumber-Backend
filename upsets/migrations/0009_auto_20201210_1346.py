# Generated by Django 3.1.2 on 2020-12-10 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upsets', '0008_remove_set_batch_update'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='set',
            index=models.Index(fields=['winner'], name='upsets_set_winner__a79627_idx'),
        ),
        migrations.AddIndex(
            model_name='set',
            index=models.Index(fields=['loser'], name='upsets_set_loser_i_13c72d_idx'),
        ),
    ]
