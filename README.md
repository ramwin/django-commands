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
pip install django-commands2
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
### AutoLogCommands
any exception will be logged in the autologcommand
```
<yourapp/management/commands/command_name.py>
from django_commands import AutoLogCommand


class Command(AutoLogCommand):

    def handle(self):
        <write your code, any exception will be logged>
```



### MultiTimesCommand
MultiTimesCommand will run multi times according to `INTERVAL` and `MAX_TIMES`. You can easily use this command to realize a crontab job every 1 second.

```python
class Command(MultiTimesCommand):
    INTERVAL = 1  # default 1
    MAX_TIMES = 60  # default 60

    def handle(self):
        <this handle function will run 60 times>
```
*This command does not consider the running time of your code. It will just run 60 times, and during each execute, wait 1 second*

### DurationCommand(AutoLogCommand):
DurationCommand will run your commands over and over again until the running time exceed the configuration
```python
import datetime

class Commmand(DurationCommand):
    INTERVAL = 1
    DURATION = datetime.timedelta(minutes=1)

    def handle(self, *args, **kwargs):
        <your code>
```

## License

`django-commands` is distributed under the terms of the ONLY USE NO PRIVATE CHANGE LICENSE license.

Anyone can use `pip install django-commands` to use this project by any meaning as long as you keep the source code unchanged.  
You are not allowed to change the source code without publishing your change.  
Here publishing means you:
    fork this project from github and keep your change available to public on the github
