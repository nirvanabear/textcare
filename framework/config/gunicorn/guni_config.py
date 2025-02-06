"""Gunicorn config file"""

# import os

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TextCare.settings')
# raw_env = ['DJANGO_SETTINGS_MODULE=TextCare.settings']

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
# wsgi_app = "TextCare.wsgi:application"
# The granularity of Error log outputs
loglevel = "debug"
# The number of worker processes for handling requests
# workers = 2
# The socket to bind
# bind = "0.0.0.0:8000"
# Restart workers when code changes (development only!)
# reload = True
# Write access and error info to /var/log
accesslog = errorlog = "/var/log/gunicorn/access_error.log"
# Redirect stdout/stderr to log file
capture_output = True
# PID file so you can easily fetch process ID
# pidfile = "/var/run/gunicorn/dev.pid"
# Daemonize the Gunicorn process (detach & enter background)
# daemon = True