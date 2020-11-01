from django.core.management.base import BaseCommand
from upsets.lib.theplayerdatabase import SqliteArchiveReader
# LOGGING
import logging
logger = logging.getLogger('cryptonavia.data_processing')


class Command(BaseCommand):
    help = 'Update data from sqlite file'

    def add_arguments(self, parser):
        parser.add_argument(
            'path',
            type=str,
            help='Path of the db sqlite file to read')

    def handle(self, *args, **options):
        path = options['path']
        reader = SqliteArchiveReader(path)
        reader.update_all_data()
