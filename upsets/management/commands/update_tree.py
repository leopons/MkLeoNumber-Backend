from django.core.management.base import BaseCommand
from upsets.lib.upsettree import UpsetTreeManager
from utils.decorators import log_exceptions
# LOGGING
import logging
logger = logging.getLogger('data_processing')


class Command(BaseCommand):
    help = 'Update upsettree from db data'

    @log_exceptions(logger)
    def handle(self, *args, **options):
        manager = UpsetTreeManager('222927')
        manager.create_from_scratch()
