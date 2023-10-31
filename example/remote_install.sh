pip3 uninstall -y django-commands2
pip3 install --index-url https://pypi.python.org/simple/ django-commands2==0.3.4
python3 manage.py test_log_command
