#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import os
import time

from django.core.management.base import BaseCommand
from django_commands.mixins import WarmShutdownMixin


class Command(WarmShutdownMixin, BaseCommand):

    def handle(self, *args, **kwargs):
        while True:
            if self.need_stop:
                print("stop")
                return
            print(f"I'm running, try run `kill -TERM {os.getpid()}` in another terminal")
            time.sleep(5)
            print("finish one loop")
