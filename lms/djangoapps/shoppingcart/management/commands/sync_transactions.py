"""
This management command will expose the ability to synchronize transactions with the Payment Provider
"""

import pytz
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from shoppingcart.sync import perform_sync
import logging

class Command(BaseCommand):
    """
    Django Management command to synchronize transactions from a payment processor

    There are two optional parameters <start_date> <end_date> that should be in month/day/year format
    """

    def handle(self, *args, **options):
        "Execute the command"
        if len(args) > 2:
            raise CommandError("sync_transactions allows for two optional parameters: <start_date> <end_date>")

        start_date = None
        if len(args) == 1:
            start_date = datetime.strptime(args[0], '%m/%d/%y')
            start_date = start_date.replace(tzinfo=pytz.UTC)

        end_date = None
        if len(args) == 2:
            end_date = datetime.strptime(args[1], '%m/%d/%y')
            end_date = end_date.replace(tzinfo=pytz.UTC)

        logger = logging.getLogger()
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(console)

        perform_sync(start_date, end_date)
