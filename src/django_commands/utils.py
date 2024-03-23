#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
datetime option
"""


import datetime
import re

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
