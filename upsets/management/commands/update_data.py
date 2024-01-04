from django.core.management.base import BaseCommand
from upsets.lib.theplayerdatabase import SqliteArchiveReader
from upsets.lib.upsettree import UpsetTreeManager
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
                  + 'Possibles are players, tournaments, sets, or trees.'))
        parser.add_argument(
            '--full',
            '-f',
            action='store_true',
            help=('Force a full backfill of the data (instead of just 6 months)'))

    @log_exceptions(logger)
    def handle(self, *args, **options):
        path = options['path']
        reader = SqliteArchiveReader(path, full_backfill=options['full'])
        tree_manager = UpsetTreeManager('222927')
        if options['object']:
            if options['object'] == 'players':
                reader.update_players()
            elif options['object'] == 'tournaments':
                reader.update_tournaments()
            elif options['object'] == 'sets':
                reader.update_sets()
            elif options['object'] == 'trees':
                tree_manager.update_all_trees()
            else:
                logger.error('Unknown object type. Possibles are players, '
                             + 'tournaments, sets, or trees.')
        else:
            reader.update_all_data()
            tree_manager.update_all_trees()
