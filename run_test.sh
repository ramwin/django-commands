#!/bin/bash
# Xiang Wang(ramwin@qq.com)

set -ex
cd example
python3 manage.py test django_commands
python3 manage.py test core.tests.test_utils
