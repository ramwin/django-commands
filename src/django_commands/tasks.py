#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import logging
from threading import Thread
from typing import Literal

from django.core.management import call_command
from celery import shared_task


LOGGER = logging.getLogger(__name__)


@shared_task
def async_call_command(
        command: str,
        using: Literal["celery", "thread", "local"]="thread",
        args=None, kwargs=None,
    ) -> None:
    args = args or []
    kwargs = kwargs or {}
    if using == "celery":
        LOGGER.info("celery task started")
        call_command(command, *args, **kwargs)
        return
    if using == "thread":
        LOGGER.info("thread task started")
        Thread(None, call_command, args=[command, *args], kwargs=kwargs).start()
        return
    if using == "local":
        LOGGER.info("local task started")
        call_command(command, *args, **kwargs)
        return
    raise NotImplementedError(using)
