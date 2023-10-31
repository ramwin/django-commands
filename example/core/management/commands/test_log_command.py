#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
test if log/error.log has logs if the command raise an exception
"""


from django_commands import AutoLogCommand


class Command(AutoLogCommand):
    """
    if you use BaseCommand, no error log will be logger.
    """

    def handle(self, *args, **kwargs):
        raise ValueError("error")
