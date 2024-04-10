#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


from django_commands.commands import WaitCommand


class Command(WaitCommand):

    def handle_task(self, *args, **kwargs):
        print("handler_task")
