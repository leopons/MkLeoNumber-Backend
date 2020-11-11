from django.core.management.base import BaseCommand
from upsets.lib.theplayerdatabase import SqliteArchiveReader
from utils.decorators import log_exceptions
# LOGGING
import logging
logger = logging.getLogger('data_processing')


class Command(BaseCommand):
    help = 'Update data from sqlite file'

    def add_arguments(self, parser):
        parser.add_argument(
            'path',
            type=str,
            help='Path of the db sqlite file to read')

    @log_exceptions(logger)
    def handle(self, *args, **options):
        path = options['path']
        reader = SqliteArchiveReader(path)
        reader.update_all_data()
