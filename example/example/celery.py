#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'example.settings')

app = Celery('proj',
             broker="redis://localhost:6379",
             )

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.result_backend = "redis://localhost:6379"

app.autodiscover_tasks()
