#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
datetime option
"""


import datetime
import re

from typing import Iterable

from django.db.models import QuerySet
from django.utils import timezone


TZ = timezone.get_default_timezone()


def datetime_type(datetimestr):
    """
    It will convert three kind of format:
        monthdaystring:
            03-22 >> 2024-03-22T00:00:00+defaulttimezone
        datestring:
            2024-03-22 >> 2024-03-22T00:00:00+defaulttimezone
        datetimestring:
            "2024-03-22 01:02:03" >> 2024-03-22T01:02:03+defaulttimezone
        isodatetimestring:
            "2024-03-22T01:02:03+04:00" >> 2024-03-22T01:02:03+04:00

    Usage:

    def add_arguments(self, parser):
        parser.add_argument("datetime", type=datetime_type)
    """
    if re.match(r"^\d{+}-\d{+}$", datetimestr):
        month, day = datetimestr.split("-")
        return datetime.datetime(
                datetime.datetime.now().year, int(month), int(day),
                0, 0, 0,
                tzinfo=TZ,
        )
    if re.match(r"^\d{4}-\d{2}-\d{2}$", datetimestr):
        year, month, day = datetimestr.split("-")
        return datetime.datetime(
                int(year), int(month), int(day),
                0, 0, 0,
                tzinfo=TZ,
        )
    datetime_obj = datetime.datetime.fromisoformat(datetimestr)
    if timezone.is_aware(datetime_obj):
        return datetime_obj
    return timezone.make_aware(datetime_obj)


def iter_large_queryset(queryset, batch_size: int = 256) -> Iterable[QuerySet]:
    """
    split queryset in batch_size, so you can use multiprocess to handler it.
    mechanism:
    1. find the offset batch_size object, get iss id
    2. use id to filter queryset, get the next batch_size offset

    so the queryset must be order by pk/id
    """
    queryset = queryset.order_by("pk")
    start_id = 0
    while True:
        try:
            end = queryset.all()[batch_size].pk
        except IndexError:
            yield queryset
            return
        result = queryset.filter(pk__gte=start_id, pk__lt=end)
        if result:
            yield result
        else:
            return
        start_id = end
        queryset = queryset.filter(pk__gte=start_id)


class Bisect:

    def __init__(self, start, end, step):
        """find first error in duration"""
        self.start = start
        self.end = end
        self.step = step
        self.checked = False

    def check(self):
        if not self.has_error(start, end):
            raise ValueError("no error between start and end")

    def has_error(self, start, end):
        raise NotImplementedError

    def find_first_error(self):
        if not self.checked:
            raise ValueError("call check before find the first error")
        start = self.start
        end = self.end
        while (end - start) > step:
            middle = self.get_middle(start, end)
            if self.has_error(start, middle):
                end = middle
            else:
                start = middle
        return start

    def get_middle(self, start, end):
        return (start + end) // 2 
