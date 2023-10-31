# SPDX-FileCopyrightText: 2023-present Xiang Wang <ramwin@qq.com>
#
# SPDX-License-Identifier: MIT


"""
some useful command sub class
"""


import logging
from django.core.management.base import BaseCommand


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
