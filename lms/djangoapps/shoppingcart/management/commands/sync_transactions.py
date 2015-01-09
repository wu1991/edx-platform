"""
This management command will expose the ability to synchronize transactions with the Payment Provider
"""

import pytz
from datetime import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from shoppingcart.sync import perform_sync
import logging


class Command(BaseCommand):
    """
    Django Management command to synchronize transactions from a payment processor

    There are three optional parameters <report_email> <start_date> <end_date>

    <start_date> and <end_date> should be in MM/DD/YY format
    """

    option_list = BaseCommand.option_list + (
        make_option('--start',
                    dest='start',
                    default=None,
                    help='Specify start date of the transaction sync'),
        make_option('--end',
                    dest='end',
                    default=None,
                    help='Specify end date of the transaction sync'),

        make_option('--mailto',
                    dest='mailto',
                    default=None,
                    help='Specify to whom to send a report email'),

        )

    def handle(self, *args, **options):
        "Execute the command"

        start = options['start']
        start_date = None
        if start:
            start_date = datetime.strptime(start, '%m/%d/%Y')
            start_date = start_date.replace(tzinfo=pytz.UTC)

        end = options['end']
        end_date = None
        if end:
            end_date = datetime.strptime(end, '%m/%d/%Y')
            end_date = end_date.replace(tzinfo=pytz.UTC)

        mailto = options['mailto']

        logger = logging.getLogger()
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(console)

        perform_sync(start_date, end_date, mailto)
