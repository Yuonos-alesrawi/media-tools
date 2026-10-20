#!/bin/sh
#entrypoint.sh
python manage.py collectstatic --noinput
python manage.py migrate --noinput
exec "$@"