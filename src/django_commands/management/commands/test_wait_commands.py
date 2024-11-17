#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import logging
from django_commands.commands import WaitCommand


LOGGER = logging.getLogger(__name__)


class Command(WaitCommand):
    SQUASH_TASK = False
    BATCH_SIZE = 2
    MAX_TIMES = 10

    def handle_task(self, taskid, **kwargs):
        LOGGER.info(taskid)
