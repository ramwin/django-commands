#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
datetime option
"""


import datetime
import itertools
import logging
import re
from graphlib import TopologicalSorter

from typing import Iterable, List

from django.db.models import QuerySet, Q, ForeignKey, Model
from django.utils import timezone


TZ = timezone.get_default_timezone()
LOGGER = logging.getLogger(__name__)


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


def iter_large_queryset(queryset, batch_size: int = 256, ordering_field: str = "pk") -> Iterable[QuerySet]:
    """
    split queryset in batch_size, so you can use multiprocess to handler it.
    mechanism:
    1. find the offset batch_size object, get iss id
    2. use id to filter queryset, get the next batch_size offset

    so the queryset must be order by pk/id
    """
    queryset = queryset.order_by(ordering_field)
    first_obj = queryset.first()
    if first_obj is None:
        return
    start_value = getattr(first_obj, ordering_field)
    while True:
        try:
            end_value = getattr(
                    queryset.all()[batch_size],
                    ordering_field,
            )
        except IndexError:
            if queryset.exists():
                yield queryset
            return
        q = Q(**{
            f"{ordering_field}__gte": start_value,
            f"{ordering_field}__lt": end_value,
        })
        result = queryset.filter(q)
        if result.exists():
            yield result
        else:
            return
        start_value = end_value
        queryset = queryset.filter(**{f"{ordering_field}__gte": start_value})


class Bisect:

    def __init__(self, start, end, step, auto_check=True):
        """find first error in duration"""
        self.start = start
        self.end = end
        self.step = step
        self._checked = False
        if auto_check:
            self.check()

    def check(self):
        if not self.has_error(self.start, self.end):
            raise ValueError("no error between start and end")
        self._checked = True

    def has_error(self, start, end):
        raise NotImplementedError

    def find_first_error(self):
        if not self._checked:
            raise ValueError("call check before find the first error")
        start = self.start
        end = self.end
        while (end - start) > self.step:
            middle = self.get_middle(start, end)
            if self.has_error(start, middle):
                end = middle
            else:
                start = middle
        return start

    def get_middle(self, start, end):
        return (start + end) // 2 


def get_middle_string(lower: str, upper: str) -> str:
    """
    return a middle value between lower and upper, in case you need to do bisect task for database field like uuid.
    """
    result = ""
    for lower_letter, upper_letter in itertools.zip_longest(lower, upper):
        if lower_letter is None:
            if ord(upper_letter) >= 32:
                return result + " "
            return result
        if lower_letter == upper_letter:
            result += lower_letter
            continue
        if ord(upper_letter) - ord(lower_letter) == 1:
            return result + lower_letter + 'a'
        return result + chr(
                (ord(upper_letter) + ord(lower_letter)) // 2
        )
    return result


class Dependency:

    def __init__(self, models, max_count=100):
        self.graph = TopologicalSorter()
        self.objects = {None}
        self.pending = set(models)
        self.max_count = max_count

    def update_objects(self) -> None:
        while self.pending:
            if len(self.objects) >= self.max_count:
                raise ValueError("too many dependencies!")
            model = self.pending.pop()
            self.objects.add(model)
            self.update_object(model)

    def update_object(self, model) -> None:
        for field in model._meta.fields:
            if not isinstance(field, ForeignKey):
                continue
            dependency = getattr(model, field.name)
            if dependency is None:
                continue
            if dependency not in self.objects:
                self.pending.add(dependency)
            self.graph.add(model, dependency)

    def all_objects(self) -> List[Model]:
        return self.graph.static_order()
