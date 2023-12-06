#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import time

from django_commands.commands import UniqueCommand


class Command(UniqueCommand):

    def handle(self):
        print("I'm running. In the next 5 seconds, you cannot execute this command.")
        time.sleep(5)
        print("I'm running")
        raise Exception("even error occurs, this task will be set finished")
