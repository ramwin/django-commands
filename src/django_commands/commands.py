#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
Usefule Command Class
"""


import datetime
import logging
import time
from decimal import Decimal
from typing import Tuple, Union

from typing import Tuple

from redis import Redis

from django.core.management.base import BaseCommand, CommandParser
from django.utils import timezone

from django_redis import get_redis_connection

import django_commands

from .mixins import AutoLogMixin, WarmShutdownMixin


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
        new_instance = django_commands.models.CommandLog.objects.create(name=unique_name)
        wait_after = timezone.now() - self.TIMEOUT
        exist_commands = django_commands.models.CommandLog.objects.filter(
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

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
                "--times", type=int, default=0,
                help="how many times do you want to execute at most")
        super().add_arguments(parser)

    def handle(self, *args, **kwargs):
        """
        get a unique name for this command
        """
        if self.IMMEDIATELY:
            self.create_task()
        redis, redis_key = self.get_redis_info()
        LOGGER.info("rpush %s to trigger task", redis_key)
        max_run_time = kwargs.get("times", 0)
        run_time = 0
        while True:
            if max_run_time and run_time >= max_run_time:
                LOGGER.info("%s has executed as least %d times, bye bye", self, run_time)
            task = redis.blpop(redis_key, timeout=5)
            if task is None:
                continue
            redis.delete(redis_key)
            self.handle_task(*args, **kwargs)
            run_time += 1

    def handle_task(self, *args, **kwargs):
        LOGGER.error("new task created, you should override this function")

    @classmethod
    def get_redis_info(cls) -> Tuple[Redis, str]:
        redis = get_redis_connection("default")
        name = cls.NAME or f"{cls.__module__}.{cls.__name__}"
        redis_key = f"django_commands_wait_command_{name}"
        return redis, redis_key

    @classmethod
    def create_task(cls) -> None:
        redis, key = cls.get_redis_info()
        redis.rpush(key, time.time())


class MultiTimesCommand(AutoLogMixin, WarmShutdownMixin, BaseCommand):
    """
    MultiTimesCommand will run multi times according to INTERVAL aND MAX_TIMES

    you can set MAX_TIMES to decimal.Decimal("inf") to run forever
    """
    INTERVAL = 1
    MAX_TIMES: Union[Decimal, int] = 60
    run_cnt = 0

    def execute(self, *args, **kwargs):
        while self.run_cnt < self.MAX_TIMES:
            self.run_cnt += 1
            super().execute(*args, **kwargs)
            time.sleep(self.INTERVAL)


class RunForeverCommand(MultiTimesCommand):
    MAX_TIMES = Decimal("inf")


class DurationCommand(AutoLogCommand):
    """
    DurationCommand will run the command multi times until the running time exceed the MAX_DURATION
    """
    INTERVAL = 1
    DURATION = datetime.timedelta(minutes=1)

    def execute(self, *args, **kwargs):
        duration = self.DURATION
        end_time = datetime.datetime.now() + duration
        LOGGER.info("end_time: %s", end_time)
        while datetime.datetime.now() < end_time:
            self.handle(*args, **kwargs)
            time.sleep(self.INTERVAL)

    def handle(self, *args, **kwargs):
        raise NotImplementedError
