# SPDX-FileCopyrightText: 2023-present Xiang Wang <ramwin@qq.com>


"""
some useful command sub class
"""


import datetime
import logging
import time
from decimal import Decimal

from django.core.management.base import BaseCommand

from .commands import (
        MultiTimesCommand,
        RunForeverCommand,
        AutoLogCommand,
        DurationCommand,
        )


LOGGER = logging.getLogger(__name__)
