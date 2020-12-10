# Generated by Django 3.1.2 on 2020-12-10 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('upsets', '0010_auto_20201210_1353'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='upsettreenode',
            name='upsets_upse_batch_u_c6cf5f_idx',
        ),
        migrations.RenameField(
            model_name='upsettreenode',
            old_name='batch_update',
            new_name='tree_container',
        ),
        migrations.AddField(
            model_name='treecontainer',
            name='offline_only',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='upsettreenode',
            unique_together={('player', 'tree_container')},
        ),
        migrations.AddIndex(
            model_name='upsettreenode',
            index=models.Index(fields=['tree_container', 'player'], name='upsets_upse_tree_co_1fac6e_idx'),
        ),
    ]