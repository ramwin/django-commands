#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>

# pylint: disable=too-few-public-methods

import logging
import signal


LOGGER = logging.getLogger(__name__)


class AutoLogMixin:

    def handle(self, *args, **kwargs):
        try:
            super().handle(*args, **kwargs)
        except Exception as error:
            LOGGER.exception(error)
            raise


class WarmShutdownMixin:
    """
    This Mixin enables your command to accept TERM signal and exist after current task finished 
    After inherit this mixin, you should add code like this:

        if self.need_stop:
            return

    in your command
    """
    need_stop = False

    def execute(self, *args, **kwargs):
        signal.signal(signal.SIGTERM, self.handle_signal)
        super().execute(*args, **kwargs)

    def handle_signal(self, signalnum, handler):  # pylint: disable=unused-argument
        LOGGER.info("receive stop signal")
        self.need_stop = True
