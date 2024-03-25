# SPDX-FileCopyrightText: 2023-present Xiang Wang <ramwin@qq.com>


"""
some useful command sub class
"""


import datetime
import logging
import time
from decimal import Decimal

from django.core.management.base import BaseCommand

from .commands import MultiTimesCommand, RunForeverCommand


LOGGER = logging.getLogger(__name__)


class AutoLogCommand(BaseCommand):
    """
    AutoLogCommand will add log to every exception and then raise it
    """

    def execute(self, *args, **kwargs):
        try:
            return super().execute(*args, **kwargs)
        except Exception as error:
            LOGGER.exception(error)
            raise

    def handle(self, *args, **kwargs):
        raise NotImplementedError


class DurationCommand(AutoLogCommand):
    """
    DurationCommand will run the command multi times until the running time exceed the MAX_DURATION
    """
    INTERVAL = 1
    DURATION = datetime.timedelta(minutes=1)

    def execute(self, *args, **kwargs):
        duration = self.DURATION
        end_time = datetime.datetime.now() + duration
        LOGGER.info("end_time: %s", end_time)
        while datetime.datetime.now() < end_time:
            self.handle(*args, **kwargs)
            time.sleep(self.INTERVAL)

    def handle(self, *args, **kwargs):
        raise NotImplementedError
