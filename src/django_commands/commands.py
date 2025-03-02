#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
Usefule Command Class
"""


import datetime
import logging
import time

from contextvars import ContextVar
from decimal import Decimal
from multiprocessing import Pool
from typing import Tuple, Union, Iterable, Optional

from redis import Redis

from django.core.management.base import BaseCommand, CommandParser
from django.db import connections
from django.db.models import QuerySet
from django.utils import timezone

from django_redis import get_redis_connection

import django_commands

from .mixins import AutoLogMixin, WarmShutdownMixin
from .utils import iter_large_queryset


PROCESS_INITED = ContextVar("inited", default=False)
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
        new_instance = django_commands.models.CommandLog.objects.create(name=unique_name)  # type: ignore[attr-defined]
        wait_after = timezone.now() - self.TIMEOUT
        exist_commands = django_commands.models.CommandLog.objects.filter(  # type: ignore[attr-defined]
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


class WaitCommand(AutoLogMixin, WarmShutdownMixin, BaseCommand):
    """
    A WaitCommand will use the redis blopop
    to run a command as soon as possible

    before start it will delete the key, so you can
    call create_task many times and only one time will it execute

    class variable:
        SQUASH_TASK = True  # wheter squash multi tasks into one
    """
    NAME = ""
    IMMEDIATELY = False
    SQUASH_TASK = True
    BATCH_SIZE = 1  # how many tasks do you want to pop once

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
                "--times", type=int, default=0,
                help="how many times do you want to execute at most")
        super().add_arguments(parser)

    def handle(self, *args, **kwargs) -> None:
        """
        get a unique name for this command
        """
        self.before_handle()
        redis, redis_key = self.get_redis_info()
        if self.IMMEDIATELY:
            LOGGER.info("rpush %s to trigger task", redis_key)
            self.create_task()
        max_run_time = kwargs.get("times", 0)
        run_time = 0
        while True:
            if self.need_stop:
                LOGGER.info("stop wait command: %s", self)
                break
            if max_run_time and run_time >= max_run_time:
                LOGGER.info("%s has executed as least %d times, bye bye", self, run_time)
                return
            if self.BATCH_SIZE == 1:
                single_task = redis.lpop(redis_key)
                if single_task:
                    key_taskids = [single_task]
                else:
                    key_taskids = []
            else:
                key_taskids = redis.lpop(redis_key, self.BATCH_SIZE)
            if not key_taskids:
                key_taskid = redis.blpop(redis_key, timeout=5)
                if key_taskid is None:
                    LOGGER.debug("no task")
                    continue
                LOGGER.debug("get one task: %s", key_taskid)
                key_taskids = [key_taskid[1]]
            else:
                LOGGER.debug("get multi task one time: %s", key_taskids)
            if self.SQUASH_TASK:
                redis.delete(redis_key)
            LOGGER.debug("handle task: %s", key_taskids)
            for key_taskid in key_taskids:
                self.handle_task(key_taskid, *args, **kwargs)
                run_time += 1

    def before_handle(self) -> None:
        """
        before handle hook
        this will be called only once
        """
        return

    def handle_task(self, task_id, *args, **kwargs) -> None:
        """
        override the handle_task function to do the real task
        """
        LOGGER.error("new task created, you should override this function")

    @classmethod
    def get_redis_info(cls) -> Tuple[Redis, str]:
        redis = get_redis_connection("default")
        redis_key = cls.NAME or f"{cls.__module__}.{cls.__name__}"
        return redis, redis_key

    @classmethod
    def create_task(cls, task_id: Optional[str] = None) -> None:
        redis, key = cls.get_redis_info()
        task_id = task_id or str(time.time())
        redis.rpush(key, task_id)

    @classmethod
    def clear_task(cls) -> None:
        redis, key = cls.get_redis_info()
        redis.delete(key)


class MultiTimesCommand(AutoLogMixin, WarmShutdownMixin, BaseCommand):
    """
    MultiTimesCommand will run multi times according to INTERVAL AND MAX_TIMES

    you can use `kill -TERM <processid>` to kill the command
    you can set MAX_TIMES to decimal.Decimal("inf") to run forever
    """
    INTERVAL = 1.0
    MAX_TIMES: Union[Decimal, int] = 60
    run_cnt = 0

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
                "--times", type=int,
                help="how many times do you want to execute at most")
        super().add_arguments(parser)

    def execute(self, *args, **kwargs):
        max_run_time = kwargs.get("times")
        if max_run_time is None:
            max_run_time = self.MAX_TIMES
        while self.run_cnt < max_run_time:
            if self.need_stop:
                break
            self.run_cnt += 1
            try:
                super().execute(*args, **kwargs)
            except StopIteration:
                break
            time.sleep(self.INTERVAL)


class RunForeverCommand(MultiTimesCommand):
    """
    Run Forever Command will run the commands forever. until you call

        kill -TERM <processid>

    """
    MAX_TIMES = Decimal("inf")


class DurationCommand(AutoLogCommand):
    """
    DurationCommand will run the command multi times until the running time exceed the MAX_DURATION(default 1 minute)
    """
    INTERVAL = 1.0
    DURATION = datetime.timedelta(minutes=1)

    def execute(self, *args, **kwargs):
        duration = self.DURATION
        end_time = datetime.datetime.now() + duration
        LOGGER.info("end_time: %s", end_time)
        while datetime.datetime.now() < end_time:
            try:
                self.handle(*args, **kwargs)
            except StopIteration:
                LOGGER.debug("StopIteration occured, DurationCommand will exit")
                break
            time.sleep(self.INTERVAL)

    def handle(self, *args, **kwargs):
        raise NotImplementedError


class MultiProcessCommand(AutoLogCommand):
    """
    A multiprocess command will use the multiprocessing.Pool to handler task.  
    You need to inherit it and custom the `get_tasks` and `handle_single_task`.  
    """

    def add_arguments(self, parser: CommandParser):
        parser.add_argument(
                "-j", "--jobs", type=int,
                help="how many process")
        super().add_arguments(parser)

    def handle(self, *args, jobs=None, **kwargs):
        start = timezone.now()
        tasks = self.get_tasks()
        LOGGER.debug("handle task: %s", tasks)
        with Pool(jobs) as p:
            for result in p.imap_unordered(
                self.handle_single_task, tasks):
                LOGGER.debug("handle single task done: %s", result)

    @classmethod
    def handle_single_task(cls, *args, **kwargs):
        """handle single task"""
        if PROCESS_INITED.get() is False:
            PROCESS_INITED.set(True)
            # connections.close_all()
        raise NotImplementedError

    def get_tasks(self):
        """return iterable task"""
        raise NotImplementedError


class LargeQuerysetMutiProcessHandlerCommand(MultiProcessCommand):
    queryset: QuerySet = None  # type: ignore[assignment]
    DURATION = datetime.timedelta(minutes=1)
    BATCH_SIZE = 256
    MAX_TASK: Union[Decimal, int] = Decimal("inf")

    def get_queryset(self):
        if self.queryset is None:
            raise ValueError("Please set queryset on the commands")
        return self.queryset

    def get_tasks(self) -> Iterable[Tuple[int, int]]:
        """use iter_large_queryset util to iterate a large queryset"""
        end_datetime = timezone.now() + self.DURATION
        results = []
        for queryset in iter_large_queryset(self.get_queryset(), self.BATCH_SIZE):
            if timezone.now() > end_datetime:
                break
            if not queryset:
                break
            first_obj = queryset.first()
            last_obj = queryset.last()
            assert first_obj
            assert last_obj
            results.append((first_obj.pk, last_obj.pk))
            if len(results) >= self.MAX_TASK:
                break
        connections.close_all()
        return results

    @classmethod
    def handle_single_task(cls, *args, **kwargs):
        """handle single task"""
        raise NotImplementedError
