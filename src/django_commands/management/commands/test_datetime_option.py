#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


from django.core.management.base import BaseCommand
from django_commands.utils import datetime_type


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("datetime", nargs="+", type=datetime_type)

    def handle(self, *args, **kwargs):
        print(kwargs["datetime"])
        pass
