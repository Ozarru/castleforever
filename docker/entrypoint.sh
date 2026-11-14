#!/bin/sh
set -eu

# Run schema migrations and collect static assets before starting Gunicorn.
# Set RUN_MIGRATIONS=0 / RUN_COLLECTSTATIC=0 for one-off maintenance containers.
if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    echo "Applying database migrations..."
    python manage.py migrate --noinput
fi

if [ "${RUN_COLLECTSTATIC:-1}" = "1" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

exec "$@"
