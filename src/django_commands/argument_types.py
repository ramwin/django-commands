#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Xiang Wang <ramwin@qq.com>


"""
useful arguments for django commands
"""


from pathlib import Path


class ExistFile(type(Path())):
    """
    exist file
    """

    def __new__(cls, *args, **kwargs):
        path = super().__new__(cls, *args, **kwargs)
        if not path.exists():
            raise FileNotFoundError(path)
        if not path.is_file():
            raise IsADirectoryError(path)
        return path


class NonExistFile(type(Path())):
    """
    file does not exist
    """

    def __new__(cls, *args, **kwargs):
        path = super().__new__(cls, *args, **kwargs)
        if path.exists():
            raise FileExistsError(path)
        return path


class Directory(type(Path())):
    """
    directory
    """

    def __new__(cls, *args, **kwargs):
        path = super().__new__(cls, *args, **kwargs)
        if not path.exists():
            raise FileNotFoundError(path)
        if not path.is_dir():
            raise NotADirectoryError(path)
        return path
