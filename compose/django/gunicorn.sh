#!/bin/sh
python /app/manage.py collectstatic --noinput
/usr/local/bin/gunicorn config.wsgi -w 4 -t 2000 -b 0.0.0.0:5000 --chdir=/app
