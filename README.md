# django-commands

[![PyPI - Version](https://img.shields.io/pypi/v/django-commands.svg)](https://pypi.org/project/django-commands)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-commands.svg)](https://pypi.org/project/django-commands)

-----

**Table of Contents**

- [Installation](#installation)
- [Usage](#Usage)
- [License](#license)

## Installation

```console
pip install django-commands
```

add django_commands to INSTALLED_APPS, and logging
```python
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
```

## Usage
* AutoLogCommands
any exception will he logger in the autologcommands
```
<yourapp/management/commands/command_name.py>
from django_commands import AutoLogCommand


class Command(AutoLogCommand):

    def handle(self):
        <write your code, any exception will be logged>
```



* MultiTimesCommands


## License

`django-commands` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
