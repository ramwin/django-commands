.. linux reference documentation master file, created by
   sphinx-quickstart on Fri Mar 29 08:41:38 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to linux reference's documentation!
===========================================

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   ./README.md


Usage
=====

#) pip install

.. code::

    pip install django-commands2


#) add django_commands to INSTALLED_APPS, and logging

.. code::
    INSTALLED_APPS = [
        ...
        'django_commands',
    ]
    LOGGING = {
        "loggers": {
            "django_commands": {
                ...your custom level, handles config...
            }
        }
    }
    DJANGO_COMMANDS_ALLOW_REMOTE_CALL = [
        "slow_command",  # add slow_command if you want to run unittest
        <your command>
    ]

#) add url config like:

.. code::

    path('api/django-commands/', include("django_commands.urls")),

#) Call Command from url

.. code::python
    requests.post("/api/django-commands/call-command", {"command": "slow_command"})


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

API Reference
=============

.. toctree::
   :maxdepth: 3

Commands
--------

.. automodule:: django_commands.commands
   :members:
   :private-members:

Mixin
-----

.. automodule:: django_commands.mixins
   :members:
   :private-members:
