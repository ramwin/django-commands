import logging
import time

from django.test import TestCase
from django_commands import models, utils
from django_commands.tasks import async_call_command

from rest_framework.test import APIClient

LOGGER = logging.getLogger(__name__)


class TestAsyncCommand(TestCase):

    def test_async(self):
        start = time.time()
        async_call_command("slow_command", using="thread")
        async_call_command("slow_command", using="thread")
        LOGGER.info("you may want run `celery -A project worker` to check if the delay is working")
        async_call_command.delay("slow_command", using="celery")
        async_call_command.delay("slow_command", using="celery")
        self.assertGreater(
                start + 1,
                time.time(),
        )

    def test_api(self):
        start = time.time()
        client = APIClient()
        res = client.post("/api/django-commands/call-command/",
                          {"command": "slow_command", "using": "thread"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {})

        self.assertGreater(
                start + 1,
                time.time(),
        )

        res = client.post("/api/django-commands/call-command/",
                          {"command": "slow_command"}, format="json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {})

        self.assertGreater(
                start + 6,
                time.time(),
        )

    def test_deny_command(self):
        client = APIClient()
        res = client.post("/api/django-commands/call-command/",
                          {"command": "non_exist_command"}, format="json")
        self.assertEqual(res.status_code, 403)


class TestUtil(TestCase):

    def test(self):
        for i in range(1000):
            models.CommandLog.objects.create(
                    name=str(i)
            )
        results = []
        for queryset in utils.iter_large_queryset(
                models.CommandLog.objects.filter(name__endswith="1")):
            results.extend([command.name for command in queryset])
        self.assertEqual(len(queryset), 100)
