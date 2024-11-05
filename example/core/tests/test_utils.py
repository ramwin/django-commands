#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


import logging

from django.test import TestCase
from core.models import Node, Leaf
from django_commands.utils import Dependency


LOGGER = logging.getLogger(__name__)


class Test(TestCase):

    def test_dependency(self):
        node = Node.objects.create(id=3)
        leaf1 = Leaf.objects.create(parent=node)
        leaf2 = Leaf.objects.create(parent=node)
        leaf3 = Leaf.objects.create(parent=node)
        dep = Dependency([leaf2, leaf1, leaf3])
        dep.update_objects()
        self.assertEqual(
            len(dep.graph._node2info[node].successors),
            3
        )
        self.assertEqual(
                list(dep.all_objects())[0],
                node,
                )
