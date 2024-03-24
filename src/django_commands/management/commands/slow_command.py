#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>

import time
import logging

from django.core.management import BaseCommand


LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        LOGGER.warning("run slow_command: begin")
        LOGGER.warning("args: %s, kwargs: %s", args, kwargs)
        time.sleep(5)
        LOGGER.warning("run slow_command: end")
