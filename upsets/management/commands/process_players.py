from django.core.management.base import BaseCommand
from django.core.paginator import Paginator
from upsets.models import Player
from utils.decorators import log_exceptions
from utils.orm_operators import BulkBatchManager
# LOGGING
import logging
logger = logging.getLogger('data_processing')


class Command(BaseCommand):
    help = 'Update players processed fields'

    @log_exceptions(logger)
    def handle(self, *args, **options):

        logger.info('Updating processed data for all players...')

        # While in a perfect world you would use queryset.iterator(), there it
        # fails to load any prefetch_related() fields specified (see docs).
        # Using Paginator() we can mimic the same functionality with prefetch

        def queryset_iterator():
            # Paginator() throws a warning if there is no sorting attached to
            # the queryset, so we sort by pk
            queryset = Player.objects \
                .all() \
                .prefetch_related('wins__tournament', 'loses__tournament') \
                .order_by('pk')
            paginator = Paginator(queryset, 2000)
            for index in range(paginator.num_pages):
                yield from paginator.get_page(index + 1)

        def player_generator(players):
            for player in players:
                player.update_main_character()
                player.update_last_tournament()
                player.update_played_sets_count()
                yield player

        batcher = BulkBatchManager(Player, logger=logger)

        batcher.bulk_update(
            player_generator(queryset_iterator()),
            ['main_character', 'last_tournament', 'played_sets_count'])

        logger.info('Done updating processed data for all players in DB.')
