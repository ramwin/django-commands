import logging
import time

from django.test import TestCase
from django_commands import models, utils
from django_commands.models import CommandLog
from django_commands.tasks import async_call_command
from django_commands.utils import get_middle_string, iter_large_queryset

from rest_framework.test import APIClient

LOGGER = logging.getLogger(__name__)


class BisectTask(utils.Bisect):
    DATA = [0, 1, 2, 3, 4, 5, 6, 8, 9, 10]

    def has_error(self, start, end):
        return (self.DATA[end] - self.DATA[start]) != end - start


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
            CommandLog.objects.create(
                    name=str(i)
            )
        iterator = iter_large_queryset(
                CommandLog.objects.filter(name__endswith="1"),
                batch_size=10)
        self.assertEqual(
            len(list(iterator)),
            10
        )
        results = []
        for queryset in iter_large_queryset(
                CommandLog.objects.filter(name__endswith="1")):
            results.extend([command.name for command in queryset])
        self.assertEqual(len(queryset), 100)

    def test_bisect(self):
        self.assertAlmostEqual(
            BisectTask(0, 9, 1).find_first_error(),
            6.5,
            delta=0.5)

    def test_get_middle_string(self):
        self.assertEqual(get_middle_string("a", "c"), "b")
        self.assertEqual(get_middle_string("", "c"), " ")
        self.assertEqual(get_middle_string("ba", "bc"), "bb")
        self.assertEqual(get_middle_string("", ""), "")
        self.assertEqual(get_middle_string("", "2"), " ")
        self.assertEqual(get_middle_string("7125811f-67c5-47f6-8327-b570b6ce72a1", "7136ec17-5a50-4d4c-a643-f3c1506bfeab"), "712a")

    def test_none_large_queryset(self):
        self.assertEqual(
            [i for i in iter_large_queryset(CommandLog.objects.all())],
            []
        )

    def test_iter_large_queryset(self):
        CommandLog.objects.create(name="bbb")
        CommandLog.objects.create(name="ccc")
        CommandLog.objects.create(name="aaa")
        a, b = iter_large_queryset(CommandLog.objects.all(), batch_size=2, ordering_field="name")
        self.assertEqual(
            b.get().name, "ccc")
