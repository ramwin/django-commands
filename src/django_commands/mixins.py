#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import logging


LOGGER = logging.getLogger(__name__)


class AutoLogMixin:

    def handle(self, *args, **kwargs):
        try:
            super().handle(*args, **kwargs)
        except Exception as error:
            LOGGER.exception(error)
            raise
