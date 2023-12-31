#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


# pylint: disable=unused-import
"""
test if log/error.log has logs if the command raise an exception
"""


import datetime
import logging
from django_commands import AutoLogCommand, MultiTimesCommand, DurationCommand
from django_commands.argument_types import ExistFile, NonExistFile, Directory


LOGGER = logging.getLogger(__name__)


class Command(AutoLogCommand):
    """
    if you use BaseCommand, no error log will be logger.
    """
    DURATION = datetime.timedelta(seconds=5)

    def add_arguments(self, parser):
        parser.add_argument("source", type=Directory)

    def handle(self, *args, **kwargs):
        LOGGER.info("run")
        # raise ValueError("error")
