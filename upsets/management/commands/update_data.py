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
        parser.add_argument(
            '--object',
            '-o',
            type=str,
            help=('Type objects to update, mainly for test purposes. '
                  + 'Possibles are players, tournaments, or sets.'))

    @log_exceptions(logger)
    def handle(self, *args, **options):
        path = options['path']
        reader = SqliteArchiveReader(path)
        if options['object']:
            if options['object'] == 'players':
                reader.update_players()
            elif options['object'] == 'tournaments':
                reader.update_tournaments()
            elif options['object'] == 'sets':
                reader.update_sets()
            else:
                logger.error('Unknown object type. Possibles are players, '
                             + 'tournaments, or sets.')
        else:
            reader.update_all_data()
