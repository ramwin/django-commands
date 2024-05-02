#!/bin/bash
# Xiang Wang(ramwin@qq.com)

rm -rf _build
sphinx-autobuild -j auto --port 18010 . _build/html/
