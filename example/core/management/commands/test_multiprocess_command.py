#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import logging
import time
from django_commands.commands import LargeQuerysetMutiProcessHandlerCommand

from django_commands.models import CommandLog


LOGGER = logging.getLogger(__name__)


class Command(LargeQuerysetMutiProcessHandlerCommand):

    queryset = CommandLog.objects.all()

    @classmethod
    def handle_single_task(cls, *args, **kwargs):
        LOGGER.info("update: %s", args[0])
        CommandLog.objects.filter(
                pk__gte=args[0][0],
                pk__lte=args[0][1],
                ).update(name=f"updated: {time.time()}")
