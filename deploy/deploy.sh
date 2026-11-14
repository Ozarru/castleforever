#!/usr/bin/env bash
# Pull the latest code and redeploy the application on the VPS.
#
# Usage (as root or as the application user):
#   cd /srv/castleforever
#   ./deploy/deploy.sh
set -euo pipefail

APP_DIR="${APP_DIR:-/srv/castleforever}"
APP_USER="${APP_USER:-castleforever}"
SERVICE_NAME="${SERVICE_NAME:-castleforever}"

cd "$APP_DIR"

# Run code and dependency changes as the application user so the checkout and
# virtualenv stay writable by Gunicorn.
run_as_app() {
    if [ "$(id -un)" = "$APP_USER" ]; then
        "$@"
    else
        sudo -u "$APP_USER" -- "$@"
    fi
}

echo "==> Pulling latest code"
run_as_app git pull --ff-only

echo "==> Installing dependencies"
run_as_app "$APP_DIR/.venv/bin/python" -m pip install --upgrade pip
run_as_app "$APP_DIR/.venv/bin/pip" install -r requirements.txt

echo "==> Applying database migrations"
run_as_app "$APP_DIR/.venv/bin/python" manage.py migrate --noinput

echo "==> Collecting static files"
run_as_app "$APP_DIR/.venv/bin/python" manage.py collectstatic --noinput

echo "==> Restarting application"
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl reload nginx

echo "==> Health check"
sleep 2
# HEALTHCHECK_HOST must match the server_name in the Nginx config.
HEALTHCHECK_HOST="${HEALTHCHECK_HOST:-example.com}"
curl --fail --silent --show-error \
    -H "Host: ${HEALTHCHECK_HOST}" \
    http://127.0.0.1/healthz/ >/dev/null
echo "Deployment completed successfully."
