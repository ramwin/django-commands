#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
Usefule Command Class
"""


import datetime
import logging
import time

from redis import Redis

from django.core.management.base import BaseCommand
from django.utils import timezone

from django_redis import get_redis_connection

from django_commands.models import CommandLog
from django_commands import AutoLogCommand

from .mixins import AutoLogMixin


LOGGER = logging.getLogger(__name__)


class UniqueCommand(AutoLogCommand):
    """
    UniqueCommand can assert that only one command instance is running

    How it works?
    Every time the command executes:
        1. it will create a django_commands.models.CommandLog instance
        2. it will check if there is another Command Instance pending with the same UNIQUE_NAME
    """
    UNIQUE_NAME = ""
    TIMEOUT = datetime.timedelta(days=1)

    def execute(self, *args, **kwargs):
        unique_name = self.get_unique_name()
        new_instance = CommandLog.objects.create(name=unique_name)
        wait_after = timezone.now() - self.TIMEOUT
        exist_commands = CommandLog.objects.filter(
                status="pending",
                name=unique_name,
                create_datetime__gte=wait_after
        ).exclude(pk=new_instance.pk)
        if exist_commands.exists():
            new_instance.status = "skipped"
            new_instance.save()
            return
        try:
            self.handle()
        finally:
            new_instance.status = "finished"
            new_instance.save()

    def get_unique_name(self) -> str:
        """
        get a unique name for this command
        """
        if self.UNIQUE_NAME:
            return self.UNIQUE_NAME
        return f"{self.__class__.__module__}.{self.__class__.__name__}"

    def handle(self, *args, **kwargs):
        raise NotImplementedError


class WaitCommand(AutoLogMixin, BaseCommand):
    """
    A WaitCommand will use the redis blopop
    to run a command as soon as possible

    before start it will delete the key, so you can
    call create_task many times and only one time will it execute
    """
    NAME = ""
    IMMEDIATELY = False

    def handle(self, *args, **kwargs):
        """
        get a unique name for this command
        """
        if self.IMMEDIATELY:
            self.create_task()
        redis, redis_key = self.get_redis_info()
        while True:
            task = redis.blpop(redis_key, timeout=5)
            if task is None:
                continue
            redis.delete(redis_key)
            self.handle_task(*args, **kwargs)

    def handle_task(self, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_redis_info(cls) -> (Redis, str):
        redis = get_redis_connection("default")
        name = cls.NAME or f"{cls.__module__}.{cls.__name__}"
        redis_key = f"django_commands_wait_command_{name}"
        return redis, redis_key

    @classmethod
    def create_task(cls) -> None:
        redis, key = cls.get_redis_info()
        redis.rpush(key, time.time())