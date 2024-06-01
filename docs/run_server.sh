#!/bin/bash
# Xiang Wang(ramwin@qq.com)

rm -rf _build
sphinx-autobuild \
    -j auto \
    --host 0.0.0.0 \
    --port 18010 \
    . \
    _build/html/
