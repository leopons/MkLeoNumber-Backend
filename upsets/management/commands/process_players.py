from django.core.management.base import BaseCommand
from upsets.models import Player
from utils.decorators import log_exceptions
# LOGGING
import logging
logger = logging.getLogger('data_processing')


class Command(BaseCommand):
    help = 'Update players processed fields'

    @log_exceptions(logger)
    def handle(self, *args, **options):
        counter = 0
        logger.info('Updating processed data for all players...')
        for player in Player.objects.all():
            player.update_main_character()
            player.update_last_tournament()
            player.update_played_sets_count()
            counter += 1
            if counter % 1000 == 0:
                logger.info('Updated processed data for %s players.' % counter)
        logger.info(
            'Done updating processed data for all %s players in DB.' % counter)
