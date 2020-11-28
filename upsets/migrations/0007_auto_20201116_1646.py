from django.db import migrations
from django.contrib.postgres.operations import UnaccentExtension


class Migration(migrations.Migration):

    dependencies = [
        ('upsets', '0006_auto_20201102_1228'),
    ]

    operations = [
        UnaccentExtension()
    ]
